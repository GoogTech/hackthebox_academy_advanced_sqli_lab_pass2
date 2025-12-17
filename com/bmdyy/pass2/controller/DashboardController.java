package com.bmdyy.pass2.controller;

import com.bmdyy.pass2.model.Credential;
import com.bmdyy.pass2.security.services.UserDetailsImpl;
import com.bmdyy.pass2.security.services.UserDetailsServiceImpl;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class DashboardController {
   @Autowired
   JdbcTemplate jdbcTemplate;
   @Autowired
   UserDetailsServiceImpl userDetailsService;
   @Value("${pass2.app.flag}")
   private String flag;

   @GetMapping({"/dashboard"})
   public String GET_Dashboard(@RequestParam(required = false) String e, Model model) {
      UserDetailsImpl userDetails = (UserDetailsImpl)SecurityContextHolder.getContext().getAuthentication().getPrincipal();
      model.addAttribute("userDetails", userDetails);
      String sql = "SELECT * FROM credentials WHERE uid = ? ORDER BY id";
      List<Credential> credentials = this.jdbcTemplate.query(sql, new Object[]{userDetails.getId()}, new BeanPropertyRowMapper(Credential.class));
      model.addAttribute("credentials", credentials);
      model.addAttribute("flag", this.flag);
      model.addAttribute("e", e);
      return "dashboard";
   }

   @PostMapping({"/dashboard/add"})
   public void POST_Dashboard_Add(HttpServletResponse response, @RequestParam String title, @RequestParam String username, @RequestParam String password) throws IOException {
      UserDetailsImpl userDetails = (UserDetailsImpl)SecurityContextHolder.getContext().getAuthentication().getPrincipal();
      String sql = "INSERT INTO credentials (uid, title, username, password) VALUES (?, ?, ?, ?)";
      this.jdbcTemplate.update(sql, new Object[]{userDetails.getId(), title, username, password});
      response.sendRedirect("/dashboard?e=Added+password!");
   }

   @PostMapping({"/dashboard/edit"})
   public void POST_Dashboard_Edit(
      HttpServletResponse response,   // Used to send HTTP redirects back to the client.
      @RequestParam String id,        // The credential ID being edited.
      @RequestParam String title,     // The new title for the credential.
      @RequestParam String username,  // The updated username for the credential.
      @RequestParam String password   // The updated password for the credential.
   ) throws IOException {

      // Retrieve the currently authenticated user from the Spring Security context.
      UserDetailsImpl userDetails = (UserDetailsImpl) SecurityContextHolder.getContext().getAuthentication().getPrincipal();
      // This will hold the credential record fetched from the database.
      Credential c;

      try {
         // Get the user's ID from the authentication object.
         Long var10000 = userDetails.getId();

         // Build an SQL query to find the credential that matches both:
         // - The current user's ID (`uid`), ensuring the credential belongs to them.
         // - The provided credential ID (`id`).
         //
         // The code removes any single quotes from `id` using `.replaceAll("'", "")`
         // to reduce injection risk — but it’s still unsafe because the query is concatenated directly.
         //
         // !!!SQL INJECTION RISK:!!!
         //   This concatenation allows injection if attackers include SQL operators or comments
         //   (e.g., `1 and 1=1`). Always use parameterized queries instead.
         String sql1 = "SELECT * FROM credentials WHERE uid = " + var10000 + " AND id = " + id.replaceAll("'", "");

         // Execute the query and map the result to a `Credential` object.
         c = (Credential) this.jdbcTemplate.queryForObject(sql1, new BeanPropertyRowMapper(Credential.class));
      } catch (Exception var9) {
         // If any exception occurs (e.g., credential not found, unauthorized access, SQL error),
         // redirect the user with an error message.
         response.sendRedirect("/dashboard?e=You+do+not+own+this+ID!");
         return;
      }

      // If the credential was found and belongs to the user:
      // Build a parameterized SQL UPDATE statement to safely update the record.
      // This one correctly uses placeholders (?) to prevent SQL injection.
      String sql2 = "UPDATE credentials SET title = ?, username = ?, password = ? WHERE id = ?";

      // Execute the update with the new field values.
      this.jdbcTemplate.update(sql2, new Object[]{title, username, password, c.getId()});

      // Redirect the user back to the dashboard with a success message.
      response.sendRedirect("/dashboard?e=Password+edited!");
   }
}
