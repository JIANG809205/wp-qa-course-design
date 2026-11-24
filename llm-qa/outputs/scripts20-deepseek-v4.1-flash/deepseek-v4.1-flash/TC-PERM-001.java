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

public class ArticlePublishPermissionTest {

    private static final String BASE_URL = "http://localhost:8080";
    private static final Duration TIMEOUT = Duration.ofSeconds(15);

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.manage().window().maximize();
        wait = new WebDriverWait(driver, TIMEOUT);
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    @Test
    public void contributorCannotSeePublishButtonOnNewArticlePage() {
        loginAsContributor("contributor", "contributor123");

        driver.get(BASE_URL + "/articles/new");

        WebElement submitForReviewButton = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("submit-for-review")));
        Assert.assertTrue(submitForReviewButton.isDisplayed(),
                "Submit-for-review button should be visible for contributor");

        List<WebElement> publishButtons = driver.findElements(By.id("publish"));
        boolean publishButtonVisible = publishButtons.stream().anyMatch(WebElement::isDisplayed);
        Assert.assertFalse(publishButtonVisible,
                "Publish button should not be visible for contributor");
    }

    private void loginAsContributor(String username, String password) {
        driver.get(BASE_URL + "/login");

        WebElement usernameInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("username")));
        usernameInput.clear();
        usernameInput.sendKeys(username);

        WebElement passwordInput = wait.until(
                ExpectedConditions.visibilityOfElementLocated(By.id("password")));
        passwordInput.clear();
        passwordInput.sendKeys(password);

        WebElement loginButton = wait.until(
                ExpectedConditions.elementToBeClickable(By.id("login-submit")));
        loginButton.click();

        wait.until(ExpectedConditions.urlContains("/dashboard"));
    }
}