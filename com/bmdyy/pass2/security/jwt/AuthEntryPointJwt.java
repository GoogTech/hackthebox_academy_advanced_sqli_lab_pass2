package com.bmdyy.pass2.security.jwt;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.stereotype.Component;

@Component
public class AuthEntryPointJwt implements AuthenticationEntryPoint {
   private static final Logger logger = LoggerFactory.getLogger(AuthEntryPointJwt.class);

   public void commence(HttpServletRequest request, HttpServletResponse response, AuthenticationException authException) throws IOException {
      logger.error("Error: {}", authException.getMessage());
      response.sendRedirect("/login");
   }
}
