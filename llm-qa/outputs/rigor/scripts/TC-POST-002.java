import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;

import java.time.Duration;

public class DraftPublishingTest {

    private WebDriver driver;

    @Test
    public void publishDraftChangesStatusToPublished() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

        By draftItem = By.cssSelector("[data-testid='draft-item']");
        By publishButton = By.cssSelector("[data-testid='publish-button']");
        By postStatus = By.cssSelector("[data-testid='post-status']");

        wait.until(ExpectedConditions.elementToBeClickable(draftItem)).click();
        wait.until(ExpectedConditions.elementToBeClickable(publishButton)).click();

        wait.until(ExpectedConditions.textToBePresentInElementLocated(postStatus, "已发布"));
        Assert.assertEquals(
                driver.findElement(postStatus).getText().trim(),
                "已发布",
                "Draft status should change to published"
        );
    }
}