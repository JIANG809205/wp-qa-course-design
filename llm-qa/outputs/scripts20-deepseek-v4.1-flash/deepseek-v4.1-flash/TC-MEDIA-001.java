import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;

import java.nio.file.Paths;
import java.time.Duration;

public class MediaUploadTest {

    @Test
    public void uploadImageShouldGenerateThumbnail() {
        WebDriver driver = new ChromeDriver();
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));

        try {
            String baseUrl = System.getProperty("baseUrl", "http://localhost:8080");
            driver.get(baseUrl + "/media");

            wait.until(ExpectedConditions.urlContains("/media"));

            WebElement mediaLibrary = wait.until(
                    ExpectedConditions.visibilityOfElementLocated(
                            By.cssSelector("[data-testid='media-library'], .media-library")
                    )
            );
            Assert.assertTrue(mediaLibrary.isDisplayed(), "Media library should be visible");

            WebElement fileInput = wait.until(
                    ExpectedConditions.presenceOfElementLocated(By.cssSelector("input[type='file']"))
            );

            String imagePath = Paths.get(
                    System.getProperty("user.dir"),
                    "src", "test", "resources", "images", "sample.jpg"
            ).toString();

            fileInput.sendKeys(imagePath);

            WebElement uploadButton = wait.until(
                    ExpectedConditions.elementToBeClickable(
                            By.cssSelector("button[data-testid='upload'], button.upload-button, button[type='submit']")
                    )
            );
            uploadButton.click();

            WebElement thumbnail = wait.until(
                    ExpectedConditions.visibilityOfElementLocated(
                            By.cssSelector("img.thumbnail, .media-thumbnail img, [data-testid='media-thumbnail'] img")
                    )
            );

            Assert.assertTrue(thumbnail.isDisplayed(), "Uploaded image thumbnail should be displayed");
            Assert.assertNotNull(thumbnail.getAttribute("src"), "Thumbnail src should not be null");
            Assert.assertFalse(thumbnail.getAttribute("src").isEmpty(), "Thumbnail src should not be empty");
        } finally {
            driver.quit();
        }
    }
}