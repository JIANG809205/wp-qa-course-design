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

public class LoginTest {

    private static final String BASE_URL = System.getProperty("baseUrl", "http://localhost:8080");
    private static final Duration TIMEOUT = Duration.ofSeconds(15);

    private WebDriver driver;
    private WebDriverWait wait;

    private static final By USERNAME_INPUT = By.id("username");
    private static final By PASSWORD_INPUT = By.id("password");
    private static final By SUBMIT_BUTTON = By.id("login-submit");
    private static final By ERROR_MESSAGE = By.cssSelector(".alert-danger, #login-error");

    @BeforeMethod(alwaysRun = true)
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

    @Test(description = "TC-AUTH-002: login fails with wrong password")
    public void shouldFailLoginWithWrongPassword() {
        driver.get(BASE_URL + "/login");

        WebElement username = wait.until(ExpectedConditions.visibilityOfElementLocated(USERNAME_INPUT));
        username.clear();
        username.sendKeys("valid_user");

        WebElement password = wait.until(ExpectedConditions.visibilityOfElementLocated(PASSWORD_INPUT));
        password.clear();
        password.sendKeys("WrongPassword123");

        wait.until(ExpectedConditions.elementToBeClickable(SUBMIT_BUTTON)).click();

        WebElement errorMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(ERROR_MESSAGE));
        String actualText = errorMessage.getText().trim();

        Assert.assertTrue(actualText.contains("密码不正确"),
                "Expected error message to contain '密码不正确' but was: " + actualText);
        Assert.assertTrue(driver.getCurrentUrl().contains("/login"),
                "User should remain on the login page after failed authentication");
    }
}