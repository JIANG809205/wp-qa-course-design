package edu.qa.wp;

import org.openqa.selenium.WebDriver;
import org.testng.ITestContext;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Listeners;

/** 所有测试的基类：创建/销毁浏览器，并把 driver 交给失败截图监听器 */
@Listeners(TestListener.class)
public abstract class BaseTest {

    protected WebDriver driver;

    @BeforeMethod(alwaysRun = true)
    public void setUp(ITestContext context) {
        driver = DriverFactory.create();
        context.setAttribute("driver", driver);
    }

    @AfterMethod(alwaysRun = true)
    public void tearDown() {
        if (driver != null) {
            driver.quit();
            driver = null;
        }
    }
}
