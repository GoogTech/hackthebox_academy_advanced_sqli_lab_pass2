package com.bmdyy.pass2.security;

import com.bmdyy.pass2.security.jwt.AuthEntryPointJwt;
import com.bmdyy.pass2.security.jwt.AuthTokenFilter;
import com.bmdyy.pass2.security.services.UserDetailsServiceImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.ExpressionUrlAuthorizationConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
@EnableGlobalMethodSecurity(
   prePostEnabled = true
)
public class WebSecurityConfig {
   @Autowired
   UserDetailsServiceImpl userDetailsService;
   @Autowired
   private AuthEntryPointJwt unauthorizedHandler;

   @Bean
   public AuthTokenFilter authenticationJwtTokenFilter() {
      return new AuthTokenFilter();
   }

   @Bean
   public DaoAuthenticationProvider authenticationProvider() {
      DaoAuthenticationProvider authProvider = new DaoAuthenticationProvider();
      authProvider.setUserDetailsService(this.userDetailsService);
      authProvider.setPasswordEncoder(this.passwordEncoder());
      return authProvider;
   }

   @Bean
   public AuthenticationManager authenticationManager(AuthenticationConfiguration authConfig) throws Exception {
      return authConfig.getAuthenticationManager();
   }

   @Bean
   public PasswordEncoder passwordEncoder() {
      return new BCryptPasswordEncoder();
   }

   @Bean
   public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
      ((ExpressionUrlAuthorizationConfigurer.AuthorizedUrl)((ExpressionUrlAuthorizationConfigurer.AuthorizedUrl)((ExpressionUrlAuthorizationConfigurer.AuthorizedUrl)((ExpressionUrlAuthorizationConfigurer.AuthorizedUrl)((ExpressionUrlAuthorizationConfigurer.AuthorizedUrl)((HttpSecurity)((HttpSecurity)((HttpSecurity)((HttpSecurity)http.cors().and()).csrf().disable()).exceptionHandling().authenticationEntryPoint(this.unauthorizedHandler).and()).sessionManagement().sessionCreationPolicy(SessionCreationPolicy.STATELESS).and()).authorizeRequests().requestMatchers(new String[]{"/login"})).permitAll().requestMatchers(new String[]{"/reset-password"})).permitAll().requestMatchers(new String[]{"/css/*"})).permitAll().requestMatchers(new String[]{"/api/v1/*"})).permitAll().anyRequest()).authenticated();
      http.authenticationProvider(this.authenticationProvider());
      http.addFilterBefore(this.authenticationJwtTokenFilter(), UsernamePasswordAuthenticationFilter.class);
      return (SecurityFilterChain)http.build();
   }
}
