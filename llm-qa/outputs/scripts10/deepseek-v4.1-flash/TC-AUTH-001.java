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

    private static final String BASE_URL = System.getProperty("baseUrl", "http://localhost:8080");
    private static final Duration TIMEOUT = Duration.ofSeconds(20);

    private WebDriver driver;
    private WebDriverWait wait;

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

    @Test(description = "TC-AUTH-001: 管理员正确登录")
    public void adminCanLoginWithValidCredentials() {
        driver.get(BASE_URL + "/wp-login.php");

        WebElement usernameInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("user_login")));
        usernameInput.clear();
        usernameInput.sendKeys("admin");

        WebElement passwordInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("user_pass")));
        passwordInput.clear();
        passwordInput.sendKeys("Admin@2026");

        WebElement submitButton = wait.until(
                ExpectedConditions.elementToBeClickable(By.id("wp-submit")));
        submitButton.click();

        boolean redirectedToWpAdmin = wait.until(
                ExpectedConditions.urlContains("/wp-admin"));

        Assert.assertTrue(redirectedToWpAdmin,
                "登录失败：期望跳转到 wp-admin，实际 URL 为 " + driver.getCurrentUrl());
        Assert.assertTrue(driver.getCurrentUrl().contains("wp-admin"),
                "当前 URL 不包含 wp-admin：" + driver.getCurrentUrl());
        Assert.assertTrue(wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("wpadminbar"))).isDisplayed(),
                "未显示 WordPress 管理工具栏");
    }
}