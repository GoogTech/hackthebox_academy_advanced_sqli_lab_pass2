## Introduction
It’s a Java SpringBoot application, used for skills assessment in Code Review, Identifying Vulnerabilities, and Advanced SQL Injections. It's developed by the HackTheBox Academy, and comes from the module of `Advanced SQL Injections`.

## How to run it
Note that you need to create the database yourself because I don't have the database source file, perhaps a powerful AI model will be your best assistant.
```java
java -jar Pass2-1.0.3-SNAPSHOT.jar
```

## App properties
```sh
spring.datasource.url= jdbc:postgresql://localhost:5432/pass2
spring.datasource.username= p2user
spring.datasource.password= 2a095344359d468f0eaeb7383da3f0362b1d225e
```

## Questions
### Question 1
Identify and exploit the unauthenticated SQL injection on the target over port `8080` to log in. What is the value of the flag on the dashboard?

### Question 2
Identify and exploit the authenticated SQL injection to get command execution on the server. What is the value of the flag in `/opt/Pass2/flag_xxxxxxxx.txt`?

## Notes
Hope my thoughts give you some tips: `/skill assessment/`
