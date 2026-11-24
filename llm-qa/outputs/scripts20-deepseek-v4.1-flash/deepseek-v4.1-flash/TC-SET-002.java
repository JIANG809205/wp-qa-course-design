import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.Duration;

public class PermalinkSettingsTest {

    private static final String BASE_URL = "http://localhost:8080";
    private static final String ADMIN_USER = "admin";
    private static final String ADMIN_PASS = "admin123";

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--start-maximized");
        driver = new ChromeDriver(options);
        wait = new WebDriverWait(driver, Duration.ofSeconds(15));
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void shouldChangePermalinkStructureToPostNameAndRedirectOldLinks() throws IOException {
        loginAsAdmin();

        driver.get(BASE_URL + "/wp-admin/options-permalink.php");

        WebElement postNameRadio = wait.until(ExpectedConditions.elementToBeClickable(
                By.cssSelector("input[name='selection'][value='/%postname%/']")));
        if (!postNameRadio.isSelected()) {
            postNameRadio.click();
        }

        WebElement saveButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("submit")));
        saveButton.click();

        WebElement notice = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.id("setting-error-settings_updated")));
        Assert.assertTrue(notice.getText().toLowerCase().contains("settings saved"),
                "Permalink structure was not saved: " + notice.getText());

        WebElement selectedRadio = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("input[name='selection'][value='/%postname%/']")));
        Assert.assertTrue(selectedRadio.isSelected(), "Post name structure is not selected after saving");

        int statusCode = getRedirectStatusCode(BASE_URL + "/?p=1");
        Assert.assertEquals(statusCode, 301,
                "Old permalink should return HTTP 301 to the new permalink, but was " + statusCode);
    }

    private void loginAsAdmin() {
        driver.get(BASE_URL + "/wp-login.php");

        WebElement userField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_login")));
        userField.clear();
        userField.sendKeys(ADMIN_USER);

        WebElement passField = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("user_pass")));
        passField.clear();
        passField.sendKeys(ADMIN_PASS);

        wait.until(ExpectedConditions.elementToBeClickable(By.id("wp-submit"))).click();

        wait.until(ExpectedConditions.presenceOfElementLocated(By.id("wpadminbar")));
    }

    private int getRedirectStatusCode(String url) throws IOException {
        HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection();
        connection.setInstanceFollowRedirects(false);
        connection.setRequestMethod("GET");
        connection.setConnectTimeout(10000);
        connection.setReadTimeout(10000);
        try {
            return connection.getResponseCode();
        } finally {
            connection.disconnect();
        }
    }
}