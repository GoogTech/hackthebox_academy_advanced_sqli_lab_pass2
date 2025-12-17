package com.bmdyy.pass2.controller;

import com.bmdyy.pass2.model.User;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Base64;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.bcrypt.BCrypt;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class ResetPasswordController {
   @Autowired
   JdbcTemplate jdbcTemplate;
   private static final Logger logger = LoggerFactory.getLogger(ResetPasswordController.class);

   // Calculate a deterministic "secret key" for the given username.
   // NOTE: This method derives a secret from user data (email + password). That has security and privacy implications
   // (see comments below). Prefer using a secure, dedicated key derivation / HMAC mechanism with proper salt.
   private String calculateSecretKey(String username) {
      try {
         // Prepare a parameterized SQL query to fetch the user by username.
         // Using a parameterized query (with '?') is good because it avoids SQL injection.
         String sql = "SELECT * FROM users WHERE username = ?";

         // Execute the query and map the single result row to a User object.
         // The `new Object[]{username}` provides the value for the '?' placeholder.
         User user = (User) this.jdbcTemplate.queryForObject(
            sql,
            new Object[]{username},
            new BeanPropertyRowMapper(User.class)
         );

         // Retrieve the user's email (stored in a temporary variable in the original code).
         String var10000 = user.getEmail();

         // Concatenate email, a fixed separator/salt "$4lty", and the stored password to form the input string.
         // tmp example: "user@example.com$4lty<hashed_password>"
         // WARNING: concatenating raw password-derived values means this function's output is tied to the password.
         String tmp = var10000 + "$4lty" + user.getPassword();

         // Create a SHA-256 MessageDigest instance to compute the hash of `tmp`.
         MessageDigest digest = MessageDigest.getInstance("SHA-256");

         // Compute the SHA-256 digest of the UTF-8 bytes of `tmp`.
         byte[] encodedHash = digest.digest(tmp.getBytes(StandardCharsets.UTF_8));

         // Encode the raw hash bytes using URL-safe Base64 encoding.
         // Then replace '-' and '_' with 'X' to further normalize characters (makes token only contain [A-Za-z0-9+/=] replaced variants).
         String b64 = Base64.getUrlEncoder().encodeToString(encodedHash).replaceAll("-|_", "X");

         // Build the "secretKey" by taking the first 16 characters of the transformed Base64 string
         // and inserting hyphens every 4 characters: "aaaa-bbbb-cccc-dddd".
         // This is purely a formatting choice and does not add cryptographic strength.
         String secretKey = String.format(
            "%s-%s-%s-%s",
            b64.substring(0, 4),
            b64.substring(4, 8),
            b64.substring(8, 12),
            b64.substring(12, 16)
         );

         // Return the formatted secret key string.
         return secretKey;
      } catch (Exception var9) {
         // On any error (user not found, SQL error, NoSuchAlgorithmException, etc.), return null.
         // Consider logging the exception (without sensitive info) or throwing a controlled exception instead.
         return null;
      }
   }

   @GetMapping({"/reset-password"})
   public String GET_Reset_Password(@RequestParam(required = false) String e, Model model) {
      model.addAttribute("e", e);
      return "reset-password";
   }

   @PostMapping({"/reset-password"})
   public void POST_Reset_Password(
      @RequestParam String username,          // The username of the account to reset.
      @RequestParam String resetKey,          // The reset key provided by the user (should match the server-calculated key).
      @RequestParam String password,          // The new password entered by the user.
      @RequestParam String repeatPassword,    // The confirmation of the new password.
      HttpServletResponse response            // Used to send HTTP redirects back to the client.
   ) throws IOException {

      // Compute the expected reset key for the given username using the internal method.
      // The key is derived from user data (email + password) via SHA-256 hashing.
      String calculatedResetKey = this.calculateSecretKey(username);

      // Log the calculated secret key for debugging.
      // WARNING: Logging secrets is insecure and should be avoided in production.
      logger.info("Calculated Secret Key: {}", calculatedResetKey);

      // If the username does not exist or an error occurred during key calculation:
      if (calculatedResetKey == null) {
         response.sendRedirect("/reset-password?e=Invalid+Username");
      }
      // If the reset key provided by the user does not match the calculated one:
      else if (!resetKey.equals(calculatedResetKey)) {
         response.sendRedirect("/reset-password?e=Invalid+Secret+Key");
      }
      // If the two password fields do not match:
      else if (!password.equals(repeatPassword)) {
         response.sendRedirect("/reset-password?e=Passwords+don't+match");
      }

      // Otherwise, all validations passed — proceed to reset the password.
      else {
         // Hash the new password using BCrypt with a cost factor of 12.
         // BCrypt automatically generates a unique salt per password.
         String passwordHash = BCrypt.hashpw(password, BCrypt.gensalt(12));

         // Prepare SQL statement to update the user's password.
         // Using parameterized query helps prevent SQL injection.
         String sql = "UPDATE users SET password = ? WHERE username = ?";

         // Execute the update with the new hashed password and username.
         this.jdbcTemplate.update(sql, new Object[]{passwordHash, username});

         // Redirect the user to the login page with a success message.
         response.sendRedirect("/login?e=Password+was+reset");
      }
   }
}
