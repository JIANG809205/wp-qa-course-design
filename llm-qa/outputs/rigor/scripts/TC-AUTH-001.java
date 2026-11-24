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

public class AdminLoginTest {

    private static final String LOGIN_URL = "http://localhost:8080/wp-login.php";
    private static final Duration TIMEOUT = Duration.ofSeconds(15);

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, TIMEOUT);
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void adminLoginWithValidCredentialsShouldOpenDashboard() {
        driver.get(LOGIN_URL);

        WebElement usernameInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("user_login")));
        usernameInput.clear();
        usernameInput.sendKeys("admin");

        WebElement passwordInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("user_pass")));
        passwordInput.clear();
        passwordInput.sendKeys("Admin@2026");

        WebElement loginButton = wait.until(
                ExpectedConditions.elementToBeClickable(By.id("wp-submit")));
        loginButton.click();

        wait.until(ExpectedConditions.urlContains("/wp-admin"));

        boolean dashboardDisplayed = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("wpadminbar"))).isDisplayed();

        Assert.assertTrue(driver.getCurrentUrl().contains("/wp-admin"),
                "Expected to be redirected to wp-admin, but current URL is: " + driver.getCurrentUrl());
        Assert.assertTrue(dashboardDisplayed, "WordPress admin bar should be visible after login");
    }
}