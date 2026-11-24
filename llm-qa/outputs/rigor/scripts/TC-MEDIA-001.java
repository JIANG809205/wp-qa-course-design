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

public class MediaUploadTest {

    private WebDriver driver;
    private WebDriverWait wait;

    private static final String BASE_URL = "https://example.com";
    private static final String IMAGE_PATH = System.getProperty("user.dir") + "/src/test/resources/images/sample-image.png";

    private static final By MEDIA_LIBRARY_MENU = By.cssSelector("a[href='/media-library']");
    private static final By MEDIA_LIBRARY_TITLE = By.cssSelector(".media-library-title");
    private static final By FILE_INPUT = By.cssSelector("input[type='file']");
    private static final By UPLOAD_BUTTON = By.cssSelector("button[data-testid='upload-button']");
    private static final By UPLOAD_SUCCESS_TOAST = By.cssSelector(".toast-success");
    private static final By MEDIA_THUMBNAIL = By.cssSelector(".media-grid .media-item .thumbnail");

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(20));
        driver.get(BASE_URL + "/login");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void uploadImageAndVerifyThumbnailGenerated() {
        wait.until(ExpectedConditions.elementToBeClickable(MEDIA_LIBRARY_MENU)).click();

        WebElement libraryTitle = wait.until(ExpectedConditions.visibilityOfElementLocated(MEDIA_LIBRARY_TITLE));
        Assert.assertTrue(libraryTitle.isDisplayed(), "Media library page should be displayed");

        WebElement fileInput = wait.until(ExpectedConditions.presenceOfElementLocated(FILE_INPUT));
        fileInput.sendKeys(IMAGE_PATH);

        wait.until(ExpectedConditions.elementToBeClickable(UPLOAD_BUTTON)).click();

        WebElement successToast = wait.until(ExpectedConditions.visibilityOfElementLocated(UPLOAD_SUCCESS_TOAST));
        Assert.assertTrue(successToast.getText().toLowerCase().contains("success"),
                "Upload success message should be shown, but was: " + successToast.getText());

        WebElement thumbnail = wait.until(ExpectedConditions.visibilityOfElementLocated(MEDIA_THUMBNAIL));
        Assert.assertTrue(thumbnail.isDisplayed(), "Thumbnail should be generated after upload");
        Assert.assertTrue(thumbnail.getAttribute("src").contains("sample-image"),
                "Thumbnail should reference the uploaded image");
    }
}