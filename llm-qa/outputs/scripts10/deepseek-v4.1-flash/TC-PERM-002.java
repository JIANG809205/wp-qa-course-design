import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedCondition;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.time.Duration;
import java.util.List;

public class SubscriberAdminAccessTest {

    private static final String BASE_URL = System.getProperty("baseUrl", "http://localhost:8080");
    private static final String SUBSCRIBER_USER = System.getProperty("subscriber.username", "subscriber");
    private static final String SUBSCRIBER_PASSWORD = System.getProperty("subscriber.password", "subscriber");
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

    @Test
    public void subscriberCannotAccessAdminEditScreen() {
        loginAsSubscriber();

        driver.get(BASE_URL + "/wp-admin/edit.php");

        wait.until((ExpectedCondition<Boolean>) d -> {
            String url = d.getCurrentUrl();
            String bodyText = d.findElement(By.tagName("body")).getText();
            boolean leftEditScreen = !url.contains("/wp-admin/edit.php");
            boolean denialMessageShown = bodyText.contains("not allowed to access this page")
                    || bodyText.contains("higher level of permission")
                    || bodyText.contains("You need a higher level");
            return leftEditScreen || denialMessageShown;
        });

        String currentUrl = driver.getCurrentUrl();
        String pageText = driver.findElement(By.tagName("body")).getText();

        boolean denialMessageShown = pageText.contains("not allowed to access this page")
                || pageText.contains("higher level of permission")
                || pageText.contains("You need a higher level");
        boolean redirectedAway = !currentUrl.contains("/wp-admin/edit.php");

        Assert.assertTrue(denialMessageShown || redirectedAway,
                "Subscriber should be denied access to /wp-admin/edit.php but reached: " + currentUrl);

        List<WebElement> postRows = driver.findElements(By.cssSelector("#the-list tr"));
        Assert.assertTrue(postRows.isEmpty(),
                "Subscriber must not see the post management list, but " + postRows.size() + " row(s) were rendered");
    }

    private void loginAsSubscriber() {
        driver.get(BASE_URL + "/wp-login.php");

        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_login")))
                .sendKeys(SUBSCRIBER_USER);
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_pass")))
                .sendKeys(SUBSCRIBER_PASSWORD);
        wait.until(ExpectedConditions.elementToBeClickable(By.id("wp-submit"))).click();

        wait.until(ExpectedConditions.or(
                ExpectedConditions.presenceOfElementLocated(By.id("wpadminbar")),
                ExpectedConditions.presenceOfElementLocated(By.id("login_error"))
        ));

        Assert.assertTrue(driver.findElements(By.id("login_error")).isEmpty(),
                "Subscriber login failed, cannot verify permission restriction");
    }
}