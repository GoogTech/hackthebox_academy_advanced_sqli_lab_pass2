package com.bmdyy.pass2.controller;

import com.bmdyy.pass2.security.jwt.JwtUtils;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class AuthController {
   @Autowired
   JdbcTemplate jdbcTemplate;
   @Autowired
   JwtUtils jwtUtils;
   @Autowired
   AuthenticationManager authenticationManager;
   @Value("${pass2.app.jwtCookieName}")
   private String jwtCookieName;
   @Value("${pass2.app.jwtExpirationMs}")
   private int jwtExpirationMs;

   @GetMapping({"/login"})
   public String GET_Login(@RequestParam(required = false) String e, @RequestParam(required = false) String logout, Model model, HttpServletResponse response) throws IOException {
      if (logout != null) {
         SecurityContextHolder.clearContext();
         Cookie jwtCookie = new Cookie(this.jwtCookieName, (String)null);
         jwtCookie.setMaxAge(0);
         jwtCookie.setHttpOnly(true);
         response.addCookie(jwtCookie);
         response.sendRedirect("/login");
      }

      model.addAttribute("e", e);
      return "login";
   }

   @PostMapping({"/login"})
   public void POST_Login(@RequestParam String username, @RequestParam String password, HttpServletResponse response) throws IOException {
      try {
         Authentication authentication = this.authenticationManager.authenticate(new UsernamePasswordAuthenticationToken(username, password));
         SecurityContextHolder.getContext().setAuthentication(authentication);
         String jwt = this.jwtUtils.generateJwtToken(authentication);
         Cookie jwtCookie = new Cookie(this.jwtCookieName, jwt);
         jwtCookie.setMaxAge(this.jwtExpirationMs);
         jwtCookie.setHttpOnly(true);
         response.addCookie(jwtCookie);
         response.sendRedirect("/dashboard");
      } catch (BadCredentialsException var7) {
         response.sendRedirect("/login?e=Invalid+username+or+password");
      }

   }
}
