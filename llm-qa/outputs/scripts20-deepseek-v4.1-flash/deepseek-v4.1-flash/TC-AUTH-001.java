package tests;

import java.time.Duration;

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

public class AdminLoginTest {

    private static final String LOGIN_URL = "https://example.com/wp-login.php";
    private static final String ADMIN_USER = "admin";
    private static final String ADMIN_PASS = "Admin@2026";

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(15));
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test(description = "TC-AUTH-001: admin logs in with valid credentials")
    public void adminLoginWithValidCredentials() {
        driver.get(LOGIN_URL);

        WebElement usernameInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("user_login")));
        usernameInput.clear();
        usernameInput.sendKeys(ADMIN_USER);

        WebElement passwordInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("user_pass")));
        passwordInput.clear();
        passwordInput.sendKeys(ADMIN_PASS);

        WebElement loginButton = wait.until(
                ExpectedConditions.elementToBeClickable(By.id("wp-submit")));
        loginButton.click();

        wait.until(ExpectedConditions.urlContains("wp-admin"));

        String currentUrl = driver.getCurrentUrl();
        Assert.assertTrue(currentUrl.contains("/wp-admin"),
                "Expected to land in wp-admin after login, but current URL was: " + currentUrl);

        WebElement adminBar = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("wpadminbar")));
        Assert.assertTrue(adminBar.isDisplayed(),
                "WordPress admin bar should be visible after a successful login");
    }
}