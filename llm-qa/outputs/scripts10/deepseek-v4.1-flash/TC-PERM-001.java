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

public class ContributorPermissionTest {

    private static final String BASE_URL = "https://example.com";
    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, Duration.ofSeconds(15));
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void contributorCannotSeePublishButtonOnNewArticlePage() {
        driver.get(BASE_URL + "/login");
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username"))).sendKeys("contributor");
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("password"))).sendKeys("P@ssw0rd");
        wait.until(ExpectedConditions.elementToBeClickable(By.id("loginButton"))).click();
        wait.until(ExpectedConditions.urlContains("/dashboard"));

        driver.get(BASE_URL + "/articles/new");
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("articleEditor")));

        WebElement submitForReviewButton = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("submitForReviewButton")));
        Assert.assertTrue(submitForReviewButton.isDisplayed(),
                "Submit-for-review button should be visible for a contributor");

        List<WebElement> publishButtons = driver.findElements(By.id("publishButton"));
        boolean publishVisible = !publishButtons.isEmpty() && publishButtons.get(0).isDisplayed();
        Assert.assertFalse(publishVisible,
                "Publish button must not be visible for a contributor");

        Assert.assertEquals(driver.findElements(By.cssSelector("button[data-action='publish']")).size(), 0,
                "No publish action should be rendered on the new article page");
    }
}