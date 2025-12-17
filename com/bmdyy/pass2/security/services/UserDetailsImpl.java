package com.bmdyy.pass2.security.services;

import com.bmdyy.pass2.model.User;
import com.fasterxml.jackson.annotation.JsonIgnore;
import java.sql.Timestamp;
import java.util.Collection;
import java.util.Objects;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;

public class UserDetailsImpl implements UserDetails {
   private static final long serialVersionUID = 1L;
   private Long id;
   private String username;
   private String email;
   @JsonIgnore
   private String password;
   private String first_name;
   private String last_name;
   private Timestamp created_at;
   private Collection authorities;

   public UserDetailsImpl(Long id, String username, String email, String password, String first_name, String last_name, Timestamp created_at, Collection authorities) {
      this.id = id;
      this.username = username;
      this.email = email;
      this.password = password;
      this.first_name = first_name;
      this.last_name = last_name;
      this.created_at = created_at;
      this.authorities = authorities;
   }

   public static UserDetailsImpl build(User user) {
      return new UserDetailsImpl(user.getId(), user.getUsername(), user.getEmail(), user.getPassword(), user.getFirst_name(), user.getLast_name(), user.getCreated_at(), (Collection)null);
   }

   public Collection getAuthorities() {
      return this.authorities;
   }

   public Long getId() {
      return this.id;
   }

   public String getEmail() {
      return this.email;
   }

   public String getFirst_name() {
      return this.first_name;
   }

   public String getLast_name() {
      return this.last_name;
   }

   public Timestamp getCreated_at() {
      return this.created_at;
   }

   public String getPassword() {
      return this.password;
   }

   public String getUsername() {
      return this.username;
   }

   public boolean isAccountNonExpired() {
      return true;
   }

   public boolean isAccountNonLocked() {
      return true;
   }

   public boolean isCredentialsNonExpired() {
      return true;
   }

   public boolean isEnabled() {
      return true;
   }

   public boolean equals(Object o) {
      if (this == o) {
         return true;
      } else if (o != null && this.getClass() == o.getClass()) {
         UserDetailsImpl user = (UserDetailsImpl)o;
         return Objects.equals(this.id, user.id);
      } else {
         return false;
      }
   }
}
