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

import java.nio.file.Paths;
import java.time.Duration;

public class MediaLibraryTest {

    private static final String BASE_URL = System.getProperty("baseUrl", "http://localhost:8080");
    private static final Duration TIMEOUT = Duration.ofSeconds(15);

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

    @Test(description = "TC-MEDIA-001 Upload image")
    public void uploadImageShouldGenerateThumbnail() {
        // Step 1: enter the media library
        driver.get(BASE_URL + "/media");
        WebElement mediaLibrary = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.cssSelector("[data-testid='media-library']")));
        Assert.assertTrue(mediaLibrary.isDisplayed(), "Media library should be visible");

        // Step 2: choose an image file
        WebElement fileInput = wait.until(
                ExpectedConditions.presenceOfElementLocated(By.cssSelector("input[type='file']")));
        String imagePath = Paths.get("src", "test", "resources", "images", "sample-image.png")
                .toAbsolutePath()
                .toString();
        fileInput.sendKeys(imagePath);
        Assert.assertTrue(fileInput.getAttribute("value").contains("sample-image.png"),
                "Selected file should be attached to the upload input");

        // Step 3: upload
        WebElement uploadButton = wait.until(
                ExpectedConditions.elementToBeClickable(By.cssSelector("[data-testid='upload-button']")));
        uploadButton.click();

        // Expected: upload succeeds and a thumbnail is generated
        WebElement thumbnail = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.cssSelector("[data-testid='media-thumbnail'] img")));
        Assert.assertTrue(thumbnail.isDisplayed(), "Thumbnail should be displayed after a successful upload");
        Assert.assertFalse(thumbnail.getAttribute("src").isEmpty(),
                "Thumbnail src should not be empty");
    }
}