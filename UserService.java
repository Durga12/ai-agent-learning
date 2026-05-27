import java.sql.*;
import java.util.*;

public class UserService {

    // Bug 1: Hardcoded DB credentials — critical security
    private String dbUrl = "jdbc:mysql://localhost:3306/mydb";
    private String dbUser = "root";
    private String dbPass = "password123";

    // Bug 2: Connection never closed — resource leak
    public List<String> getAllUsers() throws SQLException {
        Connection conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery("SELECT name FROM users");

        List<String> users = new ArrayList<>();
        while (rs.next()) {
            users.add(rs.getString("name"));
        }
        return users;  // conn never closed — memory leak
    }

    // Bug 3: SQL injection vulnerability
    public String getUserById(String userId) throws SQLException {
        Connection conn = DriverManager.getConnection(dbUrl, dbUser, dbPass);
        Statement stmt = conn.createStatement();
        // userId injected directly — SQL injection risk
        ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE id = " + userId);
        if (rs.next()) {
            return rs.getString("name");
        }
        return null;
    }

    // Bug 4: Returning null instead of Optional
    public String findEmail(String username) {
        Map<String, String> db = new HashMap<>();
        return db.get(username);  // can return null, caller not warned
    }

    // Bug 5: Swallowing exception silently
    public void deleteUser(int userId) {
        try {
            // delete logic
        } catch (Exception e) {
            // doing nothing — exception swallowed
        }
    }

    // Bug 6: No input validation
    public void createUser(String name, String email, int age) {
        // name could be empty, email invalid, age negative
        System.out.println("Creating user: " + name);
    }
}