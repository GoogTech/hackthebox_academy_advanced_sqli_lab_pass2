package com.bmdyy.pass2.controller;

import com.bmdyy.pass2.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

@Controller
public class ApiController {
   @Autowired
   JdbcTemplate jdbcTemplate;

   @GetMapping(
      value = {"/api/v1/check-user"},
      produces = {"application/json"}
   )
   
   @ResponseBody
   // This method handles a GET API request to check whether a user exists in the database.
   public String GET_API_Check_User(@RequestParam String u) {
      try {
         // Sanitize the input parameter `u` by removing potentially dangerous SQL keywords and symbols to prevent SQL injection attacks. 
         // However, this method is not fully secure because it relies on manual keyword filtering.
         u = u.replaceAll(
            " |OR|or|AND|and|LIMIT|limit|OFFSET|offset|WHERE|where|SELECT|select|UPDATE|update|" +
            "DELETE|delete|DROP|drop|CREATE|create|INSERT|insert|FUNCTION|function|CAST|cast|" +
            "ASCII|ascii|SUBSTRING|substring|VARCHAR|varchar|/\\*\\*/|;|LENGTH|length|--$",
            ""
         );

         // Construct the SQL query by concatenating the sanitized user input into the query string.
         // Still unsafe: Direct string concatenation can lead to SQL injection if input is not perfectly sanitized.
         String sql = "SELECT * FROM users WHERE username = '" + u + "'";

         // Execute the query and map the result to a `User` object.
         // `BeanPropertyRowMapper` automatically maps the columns of the result set to fields of the `User` class.
         User user = (User) this.jdbcTemplate.queryForObject(sql, new BeanPropertyRowMapper(User.class));

         // If no exception is thrown, it means the user exists — return a JSON string indicating that.
         return "{\"exists\":true}";
      } catch (Exception var4) {
         // !!! If any exception occurs (e.g., user not found, SQL error, etc.),
         // return a JSON response indicating the user does not exist.
         return "{\"exists\":false}";
      }
   }
}
