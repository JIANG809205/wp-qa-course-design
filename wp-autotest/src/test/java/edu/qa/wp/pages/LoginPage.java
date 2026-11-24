package edu.qa.wp.pages;

import java.time.Duration;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import edu.qa.wp.Config;

/** 登录页 */
public class LoginPage {

    private final WebDriver driver;
    private final WebDriverWait wait;

    private final By user = By.id("user_login");
    private final By pass = By.id("user_pass");
    private final By submit = By.id("wp-submit");
    private final By error = By.id("login_error");

    public LoginPage(WebDriver driver) {
        this.driver = driver;
        this.wait = new WebDriverWait(driver, Duration.ofSeconds(Config.WAIT_SECONDS));
    }

    public LoginPage open() {
        driver.get(Config.BASE_URL + "/wp-login.php");
        wait.until(ExpectedConditions.visibilityOfElementLocated(submit));
        return this;
    }

    public void login(String username, String password) {
        driver.findElement(user).clear();
        driver.findElement(user).sendKeys(username);
        driver.findElement(pass).clear();
        driver.findElement(pass).sendKeys(password);
        driver.findElement(submit).click();
    }

    public boolean hasError() {
        return !driver.findElements(error).isEmpty();
    }

    public String errorText() {
        return driver.findElements(error).isEmpty() ? "" : driver.findElement(error).getText();
    }

    public String currentUrl() {
        return driver.getCurrentUrl();
    }
}
