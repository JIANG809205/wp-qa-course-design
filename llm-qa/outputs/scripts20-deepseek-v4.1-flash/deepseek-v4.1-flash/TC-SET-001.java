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

public class SiteTitleSettingsTest {
    private WebDriver driver;
    private final String baseUrl = System.getProperty("baseUrl", "http://localhost:8080");

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void modifySiteTitle() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        String newTitle = "Automated Site Title " + System.currentTimeMillis();

        driver.get(baseUrl + "/admin/settings/general");

        WebElement titleInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("site-title")));
        titleInput.clear();
        titleInput.sendKeys(newTitle);

        wait.until(ExpectedConditions.elementToBeClickable(By.id("save-settings"))).click();
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector(".notice-success")));

        driver.get(baseUrl);
        WebElement frontendTitle = wait.until(ExpectedConditions.visibilityOfElementLocated(By.cssSelector("h1.site-title")));

        Assert.assertEquals(frontendTitle.getText().trim(), newTitle, "前台标题未同步更新");
    }
}