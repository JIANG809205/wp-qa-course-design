import java.time.Duration;
import java.util.List;

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

public class ContributorPermissionTest {

    private static final String BASE_URL = "http://localhost:8080";
    private static final By USERNAME_INPUT = By.id("username");
    private static final By PASSWORD_INPUT = By.id("password");
    private static final By LOGIN_BUTTON = By.id("login-submit");
    private static final By NEW_ARTICLE_LINK = By.id("new-article-link");
    private static final By PUBLISH_BUTTON = By.cssSelector("button[data-testid='publish-button'], button#publish");
    private static final By SUBMIT_REVIEW_BUTTON = By.cssSelector("button[data-testid='submit-review-button'], button#submit-review");
    private static final By ARTICLE_TITLE_INPUT = By.id("article-title");

    private WebDriver driver;
    private WebDriverWait wait;

    @BeforeMethod(alwaysRun = true)
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

    @Test(description = "TC-PERM-001: contributor cannot see publish button on new article page")
    public void contributorCannotSeePublishButtonOnNewArticlePage() {
        loginAs("contributor", "contributor123");

        WebElement newArticleLink = wait.until(ExpectedConditions.elementToBeClickable(NEW_ARTICLE_LINK));
        newArticleLink.click();

        wait.until(ExpectedConditions.visibilityOfElementLocated(ARTICLE_TITLE_INPUT));

        WebElement submitReviewButton = wait.until(
                ExpectedConditions.visibilityOfElementLocated(SUBMIT_REVIEW_BUTTON));
        Assert.assertTrue(submitReviewButton.isDisplayed(),
                "Submit-for-review button should be displayed for contributor");

        wait.until(ExpectedConditions.invisibilityOfElementLocated(PUBLISH_BUTTON));

        List<WebElement> publishButtons = driver.findElements(PUBLISH_BUTTON);
        Assert.assertTrue(publishButtons.isEmpty(),
                "Publish button must not be present for contributor, but found: " + publishButtons.size());
    }

    private void loginAs(String username, String password) {
        driver.get(BASE_URL + "/login");

        WebElement usernameField = wait.until(ExpectedConditions.visibilityOfElementLocated(USERNAME_INPUT));
        usernameField.clear();
        usernameField.sendKeys(username);

        WebElement passwordField = wait.until(ExpectedConditions.visibilityOfElementLocated(PASSWORD_INPUT));
        passwordField.clear();
        passwordField.sendKeys(password);

        wait.until(ExpectedConditions.elementToBeClickable(LOGIN_BUTTON)).click();
        wait.until(ExpectedConditions.visibilityOfElementLocated(NEW_ARTICLE_LINK));
    }
}