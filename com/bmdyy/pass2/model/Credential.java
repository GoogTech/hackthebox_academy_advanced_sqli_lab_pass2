package com.bmdyy.pass2.model;

public class Credential {
   private Long id;
   private Long uid;
   private String title;
   private String username;
   private String password;

   public Credential(Long id, Long uid, String title, String username, String password) {
      this.id = id;
      this.uid = uid;
      this.title = title;
      this.username = username;
      this.password = password;
   }

   public Credential() {
   }

   public Long getId() {
      return this.id;
   }

   public Long getUid() {
      return this.uid;
   }

   public String getTitle() {
      return this.title;
   }

   public String getUsername() {
      return this.username;
   }

   public String getPassword() {
      return this.password;
   }

   public void setId(Long id) {
      this.id = id;
   }

   public void setUid(Long uid) {
      this.uid = uid;
   }

   public void setTitle(String title) {
      this.title = title;
   }

   public void setUsername(String username) {
      this.username = username;
   }

   public void setPassword(String password) {
      this.password = password;
   }
}
