function total() {
    let sub1 = parseInt(document.getElementById("eng").value);
    let sub2 = parseInt(document.getElementById("mat").value);
    let sub3 = parseInt(document.getElementById("phy").value);
    let sub4 = parseInt(document.getElementById("urd").value);
    let sub5 = parseInt(document.getElementById("sci").value);
  
    if (sub1 > 100 || sub2 > 100 || sub3 > 100 || sub4 > 100 || sub5 > 100) {
      alert("Please Enter Marks Under 100")
    } else {
      let total = sub1 + sub2 + sub3 + sub4 + sub5;
      document.getElementById("total").innerHTML = "English:   " + sub1 + " <br> Maths:  " + sub2 + "<br> Physics:  " + sub3 + "<br> Computer:  " + sub4 + "<br> Science :  " + sub5 + "<br>_<br> Total Marks:   " + total;
    }
  }
  
  function Average() {
    let sub1 = parseInt(document.getElementById("eng").value);
    let sub2 = parseInt(document.getElementById("mat").value);
    let sub3 = parseInt(document.getElementById("phy").value);
    let sub4 = parseInt(document.getElementById("urd").value);
    let sub5 = parseInt(document.getElementById("sci").value);
  
    if (sub1 > 100 || sub2 > 100 || sub3 > 100 || sub4 > 100 || sub5 > 100) {
      alert("Please Enter Marks Under 100")
    } else {
      let total = sub1 + sub2 + sub3 + sub4 + sub5;
      let Ave = total / 5;
      document.getElementById("ave").innerHTML = "Your Average Marks is :" + Ave.toFixed(2);
    }
  }
  
  function grade() {
    let sub1 = parseInt(document.getElementById("eng").value);
    let sub2 = parseInt(document.getElementById("mat").value);
    let sub3 = parseInt(document.getElementById("phy").value);
    let sub4 = parseInt(document.getElementById("urd").value);
    let sub5 = parseInt(document.getElementById("sci").value);
  
    if (sub1 > 100 || sub2 > 100 || sub3 > 100 || sub4 > 100 || sub5 > 100) {
      alert("Please Enter Marks Under 100")
    } else {
      let total = sub1 + sub2 + sub3 + sub4 + sub5;
      let Ave = total / 5;
  
      let grade = "";
  
      if (Ave >= 90) {
        grade = "A";
      } else if (Ave >= 80) {
        grade = "B";
      } else if (Ave >= 70) {
        grade = "C";
      } else if (Ave >= 60) {
        grade = "D";
      } else {
        grade = "F";
      }
  
      document.getElementById("grade").innerHTML = "Your Grade is: " + grade;
    }
  }
  