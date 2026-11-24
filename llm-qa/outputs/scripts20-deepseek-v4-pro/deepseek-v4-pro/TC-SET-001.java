import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.AfterClass;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

import java.time.Duration;

public class SiteTitleTest {
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeClass
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void testUpdateSiteTitle() {
        driver.get("https://example.com/wp-admin/options-general.php");

        WebElement titleInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("blogname")));

        String newTitle = "Updated Title " + System.currentTimeMillis();
        titleInput.clear();
        titleInput.sendKeys(newTitle);

        WebElement saveButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("submit")));
        saveButton.click();

        wait.until(ExpectedConditions.visibilityOfElementLocated(By.xpath("//div[contains(@class,'notice-success')]")));

        driver.get("https://example.com/");
        wait.until(ExpectedConditions.titleContains(newTitle));
        String actualTitle = driver.getTitle();
        Assert.assertTrue(actualTitle.contains(newTitle), "前台标题未更新：" + actualTitle);
    }

    @AfterClass
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}