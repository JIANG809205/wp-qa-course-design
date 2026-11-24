import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import org.testng.Assert;
import org.testng.annotations.Test;

import java.time.Duration;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class ScheduledPostTest {

    private WebDriver driver;

    @Test
    public void schedulePostForFutureTime() {
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(15));

        wait.until(ExpectedConditions.elementToBeClickable(By.id("new-post"))).click();

        WebElement titleInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("post-title")));
        titleInput.clear();
        titleInput.sendKeys("Scheduled Post " + System.currentTimeMillis());

        WebElement contentInput = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("post-content")));
        contentInput.clear();
        contentInput.sendKeys("Scheduled post content");

        wait.until(ExpectedConditions.elementToBeClickable(By.id("schedule-post"))).click();

        String futureDateTime = LocalDateTime.now()
                .plusDays(1)
                .withHour(10)
                .withMinute(0)
                .withSecond(0)
                .withNano(0)
                .format(DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm"));

        WebElement scheduleDateTimeInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("schedule-datetime")));
        scheduleDateTimeInput.clear();
        scheduleDateTimeInput.sendKeys(futureDateTime);

        wait.until(ExpectedConditions.elementToBeClickable(By.id("save-post"))).click();

        WebElement scheduledStatus = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.xpath("//*[contains(normalize-space(text()), '已安排')]")));

        Assert.assertTrue(scheduledStatus.isDisplayed(), "文章状态应为已安排");
        Assert.assertTrue(scheduledStatus.getText().contains("已安排"), "文章状态应为已安排");
    }
}