import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;
import java.time.Duration;

public class TC_AUTH_001_Test {
    WebDriver driver;
    WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void testAdminLogin() {
        driver.get("http://localhost/wp-login.php"); // 替换为实际登录页地址

        WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_login")));
        usernameField.sendKeys("admin");

        WebElement passwordField = driver.findElement(By.id("user_pass"));
        passwordField.sendKeys("Admin@2026");

        WebElement loginButton = driver.findElement(By.id("wp-submit"));
        loginButton.click();

        wait.until(ExpectedConditions.urlContains("/wp-admin"));

        String currentUrl = driver.getCurrentUrl();
        Assert.assertTrue(currentUrl.contains("/wp-admin"),
                "登录后URL应包含/wp-admin，但实际为：" + currentUrl);
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}