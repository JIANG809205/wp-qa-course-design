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
import java.util.List;

public class ContributorPublishPermissionTest {

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(10));
    }

    @Test
    public void contributorCannotSeePublishButtonOnNewArticlePage() {
        driver.get("https://example.com/login");

        wait.until(ExpectedConditions.visibilityOfElementLocated(By.name("username")))
                .sendKeys("contributor");
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.name("password")))
                .sendKeys("password");
        wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("button[type='submit']")))
                .click();

        wait.until(ExpectedConditions.urlContains("/dashboard"));

        driver.get("https://example.com/articles/new");
        wait.until(ExpectedConditions.urlContains("/articles/new"));

        WebElement submitReviewButton = wait.until(ExpectedConditions.visibilityOfElementLocated(
                By.xpath("//button[normalize-space()='提交复审' or normalize-space()='Submit for review']")));
        Assert.assertTrue(submitReviewButton.isDisplayed(), "Submit for review button should be visible");

        List<WebElement> publishButtons = driver.findElements(
                By.xpath("//button[normalize-space()='发布' or normalize-space()='Publish']"));
        boolean publishVisible = publishButtons.stream().anyMatch(WebElement::isDisplayed);

        Assert.assertFalse(publishVisible, "Publish button must not be visible for contributor");
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}