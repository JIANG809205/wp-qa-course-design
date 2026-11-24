package tests;

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

public class CommentSubmissionTest {

    private static final String BASE_URL = System.getProperty("base.url", "http://localhost:8080");
    private static final Duration TIMEOUT = Duration.ofSeconds(20);

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

    @Test(description = "TC-COMM-001: submitting a comment should put it into pending review")
    public void submitCommentShouldEnterPendingReview() {
        driver.get(BASE_URL + "/articles/1");

        WebElement commentInput = wait.until(
                ExpectedConditions.elementToBeClickable(By.cssSelector("textarea[name='comment']")));
        commentInput.clear();
        commentInput.sendKeys("Automated comment submitted by TestNG.");

        WebElement submitButton = wait.until(
                ExpectedConditions.elementToBeClickable(By.cssSelector("button[type='submit']")));
        submitButton.click();

        WebElement reviewNotice = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.xpath("//*[contains(normalize-space(text()),'等待审核')]")));

        Assert.assertTrue(reviewNotice.isDisplayed(),
                "The pending-review notice should be visible after submitting a comment.");
        Assert.assertTrue(reviewNotice.getText().contains("等待审核"),
                "The notice should tell the user the comment is awaiting review, but was: " + reviewNotice.getText());

        WebElement submitDisabledOrCleared = wait.until(
                ExpectedConditions.presenceOfElementLocated(By.cssSelector("textarea[name='comment']")));
        Assert.assertEquals(submitDisabledOrCleared.getAttribute("value"), "",
                "The comment textarea should be cleared after the comment is submitted.");
    }
}