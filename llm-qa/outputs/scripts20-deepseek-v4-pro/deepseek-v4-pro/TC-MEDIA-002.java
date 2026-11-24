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

public class MediaLibraryTest {
    WebDriver driver;
    WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void testUploadOversizedFile() {
        driver.get("http://example.com/media");
        WebElement fileInput = driver.findElement(By.id("fileUpload"));
        fileInput.sendKeys("/path/to/20MB-image.jpg");
        WebElement uploadButton = driver.findElement(By.id("uploadBtn"));
        uploadButton.click();
        WebElement errorMsg = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("errorMessage")));
        Assert.assertTrue(errorMsg.getText().contains("超过大小限制"));
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}