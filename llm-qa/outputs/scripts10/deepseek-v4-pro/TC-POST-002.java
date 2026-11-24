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

public class PublishDraftTest {
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void testPublishDraft() {
        driver.get("http://example.com/drafts");
        WebElement draftLink = wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//a[text()='Draft Title']")));
        draftLink.click();

        WebElement publishButton = wait.until(ExpectedConditions.elementToBeClickable(By.id("publish-button")));
        publishButton.click();

        WebElement statusLabel = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("post-status")));
        Assert.assertEquals(statusLabel.getText(), "已发布", "Status should be '已发布'");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}