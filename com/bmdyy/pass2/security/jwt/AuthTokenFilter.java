package com.bmdyy.pass2.security.jwt;

import com.bmdyy.pass2.security.services.UserDetailsServiceImpl;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.web.filter.OncePerRequestFilter;

public class AuthTokenFilter extends OncePerRequestFilter {
   @Autowired
   private JwtUtils jwtUtils;
   @Autowired
   private UserDetailsServiceImpl userDetailsService;
   @Value("${pass2.app.jwtCookieName}")
   private String jwtCookieName;
   private static final Logger logger = LoggerFactory.getLogger(AuthTokenFilter.class);

   protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {
      try {
         String jwt = this.parseJwt(request);
         if (jwt != null && this.jwtUtils.validateJwtToken(jwt)) {
            String username = this.jwtUtils.getUsernameFromJwtToken(jwt);
            UserDetails userDetails = this.userDetailsService.loadUserByUsername(username);
            UsernamePasswordAuthenticationToken authentication = new UsernamePasswordAuthenticationToken(userDetails, (Object)null, userDetails.getAuthorities());
            authentication.setDetails((new WebAuthenticationDetailsSource()).buildDetails(request));
            SecurityContextHolder.getContext().setAuthentication(authentication);
         }
      } catch (Exception e) {
         logger.error("Cannot set user authentication: {}", e.getMessage());
      }

      filterChain.doFilter(request, response);
   }

   private String parseJwt(HttpServletRequest request) {
      if (request.getCookies() == null) {
         return null;
      } else {
         for(Cookie cookie : request.getCookies()) {
            if (cookie.getName().equals(this.jwtCookieName)) {
               return cookie.getValue();
            }
         }

         return null;
      }
   }
}
