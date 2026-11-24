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

public class SubscriberAdminAccessTest {

    private static final String BASE_URL = "http://localhost:8888";
    private static final String SUBSCRIBER_USER = "subscriber_user";
    private static final String SUBSCRIBER_PASS = "subscriber_pass";

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod(alwaysRun = true)
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(20));
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test(description = "TC-PERM-002: subscriber must not be able to enter wp-admin")
    public void subscriberCannotAccessAdminDashboard() {
        driver.get(BASE_URL + "/wp-login.php");

        WebElement userLogin = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_login")));
        userLogin.clear();
        userLogin.sendKeys(SUBSCRIBER_USER);

        WebElement userPass = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_pass")));
        userPass.clear();
        userPass.sendKeys(SUBSCRIBER_PASS);

        WebElement submit = wait.until(ExpectedConditions.elementToBeClickable(By.id("wp-submit")));
        submit.click();

        wait.until(ExpectedConditions.urlContains("/wp-admin/"));

        driver.get(BASE_URL + "/wp-admin/edit.php");

        Boolean denied = wait.until(ExpectedConditions.or(
                ExpectedConditions.visibilityOfElementLocated(By.id("wp-die-message")),
                ExpectedConditions.textToBePresentInElementLocated(
                        By.tagName("body"), "Sorry, you are not allowed to access this page."),
                ExpectedConditions.titleContains("Forbidden")
        ));

        Assert.assertTrue(Boolean.TRUE.equals(denied), "Subscriber should be denied access to /wp-admin/edit.php");

        boolean postsTableRendered = driver.getPageSource().contains("wp-list-table");
        Assert.assertFalse(postsTableRendered, "Posts list table should not be rendered for a subscriber");
    }
}