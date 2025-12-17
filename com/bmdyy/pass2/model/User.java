package com.bmdyy.pass2.model;

import com.fasterxml.jackson.annotation.JsonIgnore;
import java.sql.Timestamp;

public class User {
   private Long id;
   private String username;
   private String email;
   @JsonIgnore
   private String password;
   private String first_name;
   private String last_name;
   private Timestamp created_at;

   public User(Long id, String username, String email, String password, String first_name, String last_name, Timestamp created_at) {
      this.id = id;
      this.username = username;
      this.email = email;
      this.password = password;
      this.first_name = first_name;
      this.last_name = last_name;
      this.created_at = created_at;
   }

   public User() {
   }

   public Long getId() {
      return this.id;
   }

   public String getUsername() {
      return this.username;
   }

   public String getEmail() {
      return this.email;
   }

   public String getPassword() {
      return this.password;
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

   public void setId(Long id) {
      this.id = id;
   }

   public void setUsername(String username) {
      this.username = username;
   }

   public void setEmail(String email) {
      this.email = email;
   }

   public void setPassword(String password) {
      this.password = password;
   }

   public void setCreated_at(Timestamp created_at) {
      this.created_at = created_at;
   }

   public void setFirst_name(String first_name) {
      this.first_name = first_name;
   }

   public void setLast_name(String last_name) {
      this.last_name = last_name;
   }
}
