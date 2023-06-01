*** Settings ***
Library    SeleniumLibrary
Library    OperatingSystem

*** Variables ***
${BROWSER}    chrome
${URL}        http://127.0.0.1:5000

*** Test Cases ***
Register User
    Open Browser    ${URL}    ${BROWSER}
    Click Link    Register
    Input Text    username    testuser
    Input Text    password    testpassword
    Input Text    email    testuser@example.com
    Click Button    Submit
    Page Should Contain    You have successfully registered!
    Close Browser

Login User
    Open Browser    ${URL}    ${BROWSER}
    Click Link    Login
    Input Text    username    testuser
    Input Text    password    testpassword
    Click Button    Submit
    Page Should Contain    Welcome, testuser!
    Close Browser

Create Post
    Open Browser    ${URL}    ${BROWSER}
    Click Link    Login
    Input Text    username    testuser
    Input Text    password    testpassword
    Click Button    Submit
    Click Link    New Post
    Input Text    title    Test Post
    Input Text    content    This is a test post.
    Click Button    Submit
    Page Should Contain    Test Post
    Click Element    //a[h2='Test Post']
    Page Should Contain    This is a test post.
    Close Browser

Edit Post
    Open Browser    ${URL}    ${BROWSER}
    Click Link    Login
    Input Text    username    testuser
    Input Text    password    testpassword
    Click Button    Submit
    Click Element    //a[h2='Test Post']
    Click Element    //a[@href='/3/edit']//span[@class='badge badge-warning']
    Input Text    title    Updated Post
    Input Text    content    This post has been updated.
    Click Button    Submit
    Page Should Contain    Updated Post
    Close Browser

Delete Post
    Open Browser    ${URL}    ${BROWSER}
    Click Link    Login
    Input Text    username    testuser
    Input Text    password    testpassword
    Click Button    Submit
    Click Element    //a[h2='Updated Post']
    Click Element    //a[@href='/3/edit']//span[@class='badge badge-warning']
    Click Button    //form[@action='/3/delete']//input[@value='Delete Post']
    Handle Alert    Accept
    Page Should Contain    "Updated Post" was successfully deleted!
    Close Browser
