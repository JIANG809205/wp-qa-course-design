import java.nio.file.Paths;
import java.time.Duration;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;

public class MediaLibraryUploadTest {

    private WebDriver driver;

    private static final String BASE_URL = "https://example.com";
    private static final String MEDIA_LIBRARY_PATH = "/media";
    private static final String OVERSIZED_IMAGE_PATH = "src/test/resources/media/oversized-20MB-image.jpg";
    private static final Duration DEFAULT_TIMEOUT = Duration.ofSeconds(20);

    private WebDriverWait waitFor() {
        return new WebDriverWait(driver, DEFAULT_TIMEOUT);
    }

    @Test
    public void uploadFileExceedingSizeLimit() {
        driver.get(BASE_URL + MEDIA_LIBRARY_PATH);

        WebDriverWait wait = waitFor();

        WebElement mediaLibrary = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("[data-testid='media-library']")));
        Assert.assertTrue(mediaLibrary.isDisplayed(), "Media library should be visible after navigation");

        WebElement fileInput = wait.until(ExpectedConditions.presenceOfElementLocated(
                By.cssSelector("input[type='file']")));
        fileInput.sendKeys(Paths.get(OVERSIZED_IMAGE_PATH).toAbsolutePath().toString());

        WebElement uploadButton = wait.until(ExpectedConditions.elementToBeClickable(
                By.cssSelector("[data-testid='upload-button']")));
        uploadButton.click();

        WebElement errorMessage = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.cssSelector("[data-testid='upload-error']")));
        String errorText = errorMessage.getText().trim();
        String normalized = errorText.toLowerCase();

        Assert.assertFalse(errorText.isEmpty(), "File size limit error message should be displayed");
        Assert.assertTrue(
                normalized.contains("size") || normalized.contains("limit") || normalized.contains("too large"),
                "Expected a file size limit error but got: " + errorText);
    }
}