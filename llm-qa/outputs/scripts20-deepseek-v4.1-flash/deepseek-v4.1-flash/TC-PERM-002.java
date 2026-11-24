import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;

import java.time.Duration;

public class SubscriberAdminAccessTest {
    private static final String BASE_URL = System.getProperty("baseUrl", "http://localhost");
    private static final String SUBSCRIBER_USERNAME = System.getProperty("subscriberUsername", "subscriber");
    private static final String SUBSCRIBER_PASSWORD = System.getProperty("subscriberPassword", "password");

    @Test
    public void subscriberCannotAccessAdminEditPage() {
        WebDriver driver = new ChromeDriver();
        try {
            WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
            loginAsSubscriber(driver, wait);

            driver.get(BASE_URL + "/wp-admin/edit.php");

            wait.until(d -> d.getCurrentUrl().contains("wp-login.php")
                    || d.getCurrentUrl().contains("/wp-admin/profile.php")
                    || d.getPageSource().contains("Sorry, you are not allowed to access this page.")
                    || !d.findElements(By.id("error-page")).isEmpty());

            String currentUrl = driver.getCurrentUrl();
            String pageSource = driver.getPageSource();
            boolean denied = currentUrl.contains("wp-login.php")
                    || currentUrl.contains("/wp-admin/profile.php")
                    || pageSource.contains("Sorry, you are not allowed to access this page.")
                    || !driver.findElements(By.id("error-page")).isEmpty();

            Assert.assertTrue(denied, "Subscriber must be denied access to /wp-admin/edit.php. Current URL: " + currentUrl);
        } finally {
            driver.quit();
        }
    }

    private void loginAsSubscriber(WebDriver driver, WebDriverWait wait) {
        driver.get(BASE_URL + "/wp-login.php");
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_login"))).sendKeys(SUBSCRIBER_USERNAME);
        driver.findElement(By.id("user_pass")).sendKeys(SUBSCRIBER_PASSWORD);
        driver.findElement(By.id("wp-submit")).click();
        wait.until(ExpectedConditions.not(ExpectedConditions.urlContains("wp-login.php")));
    }
}