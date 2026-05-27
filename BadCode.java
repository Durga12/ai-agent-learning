import java.util.*;

public class BadCode {

    // Bug 1: No null check — NPE waiting to happen
    public String getUserName(Map<String, String> user) {
        return user.get("name").toUpperCase();
    }

    // Bug 2: Catching generic Exception — hides real errors
    public void readFile(String path) {
        try {
            // file reading logic here
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // Bug 3: String concatenation in loop — performance killer
    // should use StringBuilder
    public String buildReport(List<String> items) {
        String result = "";
        for (String item : items) {
            result = result + item + "\n";
        }
        return result;
    }

    // Bug 4: Public field — breaks encapsulation completely
    public List<String> userData = new ArrayList<>();

    // Bug 5: No division by zero check — ArithmeticException
    public int divide(int a, int b) {
        return a / b;
    }

    // Bug 6: Hardcoded password — critical security risk
    private String password = "admin123";

    // Bug 7: Using == to compare strings — classic Java mistake
    public boolean checkStatus(String status) {
        if (status == "active") {
            return true;
        }
        return false;
    }

    // Bug 8: Empty catch block — swallows exception silently
    public void processData(String data) {
        try {
            int value = Integer.parseInt(data);
            System.out.println(value);
        } catch (NumberFormatException e) {
            // doing nothing — silent failure
        }
    }

    // Bug 9: Returning null — forces caller to null check
    public String findUser(String id) {
        Map<String, String> users = new HashMap<>();
        return users.get(id); // can return null
    }

    // Bug 10: Magic numbers — no constants defined
    public double calculateDiscount(double price) {
        if (price > 1000) {
            return price * 0.15; // what is 1000? what is 0.15?
        }
        return price * 0.05;
    }
}