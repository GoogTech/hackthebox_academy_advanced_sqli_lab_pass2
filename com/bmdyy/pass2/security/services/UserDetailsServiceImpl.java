package com.bmdyy.pass2.security.services;

import com.bmdyy.pass2.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

@Service
public class UserDetailsServiceImpl implements UserDetailsService {
   @Autowired
   JdbcTemplate jdbcTemplate;

   public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
      User user;
      try {
         String sql = "SELECT * FROM users WHERE username = ?";
         user = (User)this.jdbcTemplate.queryForObject(sql, new Object[]{username}, new BeanPropertyRowMapper(User.class));
      } catch (Exception var4) {
         throw new UsernameNotFoundException("User not found with username: " + username);
      }

      return UserDetailsImpl.build(user);
   }
}
