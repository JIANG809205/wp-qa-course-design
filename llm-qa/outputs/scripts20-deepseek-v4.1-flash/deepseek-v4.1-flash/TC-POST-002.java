import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

import java.time.Duration;

public class PostDraftPublishTest {

    private WebDriver driver;
    private WebDriverWait wait;

    private static final By DRAFT_ITEM = By.cssSelector("[data-testid='draft-item']");
    private static final By PUBLISH_BUTTON = By.cssSelector("[data-testid='publish-button']");
    private static final By STATUS_LABEL = By.cssSelector("[data-testid='post-status']");
    private static final By CONFIRM_DIALOG_BUTTON = By.cssSelector("[data-testid='confirm-publish']");

    @BeforeMethod
    public void setUp() {
        driver = DriverFactory.createDriver();
        wait = new WebDriverWait(driver, Duration.ofSeconds(15));
        driver.manage().window().maximize();
        driver.get(Config.getBaseUrl() + "/posts/drafts");
    }

    @Test(description = "TC-POST-002: Publish a draft post and verify status becomes published")
    public void publishDraftPost() {
        WebElement draft = wait.until(ExpectedConditions.elementToBeClicked(DRAFT_ITEM));

        By titleOfDraft = By.xpath(".//*[@data-testid='post-title']");
        String draftTitle = draft.findElement(titleOfDraft).getText().trim();
        Assert.assertFalse(draftTitle.isEmpty(), "Draft title should not be empty");

        draft.click();

        WebElement publishButton = wait.until(ExpectedConditions.elementToBeClickable(PUBLISH_BUTTON));
        wait.until(ExpectedConditions.visibilityOf(publishButton));
        Assert.assertTrue(publishButton.isEnabled(), "Publish button should be enabled");
        publishButton.click();

        wait.until(ExpectedConditions.elementToBeClickable(CONFIRM_DIALOG_BUTTON)).click();

        WebElement status = wait.until(ExpectedConditions.visibilityOfElementLocated(STATUS_LABEL));
        wait.until(ExpectedConditions.textToBePresentInElement(status, "Published"));

        Assert.assertEquals(status.getText().trim(), "Published",
                "Post status should change to 'Published' after publishing the draft");
    }
}