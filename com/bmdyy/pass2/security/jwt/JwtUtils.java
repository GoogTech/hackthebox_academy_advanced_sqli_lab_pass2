package com.bmdyy.pass2.security.jwt;

import com.bmdyy.pass2.security.services.UserDetailsImpl;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.SignatureException;
import io.jsonwebtoken.UnsupportedJwtException;
import java.util.Date;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

@Component
public class JwtUtils {
   private static final Logger logger = LoggerFactory.getLogger(JwtUtils.class);
   @Value("${pass2.app.jwtSecret}")
   private String jwtSecret;
   @Value("${pass2.app.jwtExpirationMs}")
   private int jwtExpirationMs;

   public String generateJwtToken(Authentication authentication) {
      UserDetailsImpl userPrincipal = (UserDetailsImpl)authentication.getPrincipal();
      return Jwts.builder().setSubject(userPrincipal.getUsername()).setIssuedAt(new Date()).setExpiration(new Date((new Date()).getTime() + (long)this.jwtExpirationMs)).signWith(SignatureAlgorithm.HS512, this.jwtSecret).compact();
   }

   public String getUsernameFromJwtToken(String token) {
      return ((Claims)Jwts.parser().setSigningKey(this.jwtSecret).parseClaimsJws(token).getBody()).getSubject();
   }

   public boolean validateJwtToken(String authToken) {
      try {
         Jwts.parser().setSigningKey(this.jwtSecret).parseClaimsJws(authToken);
         return true;
      } catch (SignatureException e) {
         logger.error("Invalid JWT Signature: {}", e.getMessage());
      } catch (MalformedJwtException e) {
         logger.error("Invalid JWT: {}", e.getMessage());
      } catch (ExpiredJwtException e) {
         logger.error("JWT is expired: {}", e.getMessage());
      } catch (UnsupportedJwtException e) {
         logger.error("JWT is unsupported: {}", e.getMessage());
      } catch (IllegalArgumentException e) {
         logger.error("JWT claims string is empty: {}", e.getMessage());
      }

      return false;
   }
}
