import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;

import java.time.Duration;

public class DraftPublishTest {

    private WebDriver driver;

    @Test
    public void publishDraftChangesStatusToPublished() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));

        wait.until(ExpectedConditions.elementToBeClickable(
                By.xpath("//*[normalize-space()='草稿' or normalize-space()='草稿箱']")
        )).click();

        wait.until(ExpectedConditions.elementToBeClickable(
                By.xpath("//button[normalize-space()='发布' or normalize-space()='发布草稿']")
        )).click();

        WebElement publishedStatus = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.xpath("//*[contains(@class,'status') and normalize-space()='已发布']")
        ));

        Assert.assertEquals(publishedStatus.getText().trim(), "已发布", "草稿发布后状态应变为已发布");
    }
}