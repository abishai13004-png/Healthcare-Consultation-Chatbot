/* CareBridge AI frontend — connects to the existing Flask API */
const chatBox=document.getElementById("chatBox");
const chatForm=document.getElementById("chatForm");
const userInput=document.getElementById("userInput");
const sendButton=document.getElementById("sendButton");
const clearButton=document.getElementById("clearChat");
const typingIndicator=document.getElementById("typingIndicator");
const historyList=document.getElementById("historyList");
const historyCount=document.getElementById("historyCount");
const welcomeBlock=document.getElementById("welcomeBlock");
const suggestions=document.getElementById("suggestions");

function updateIntroVisibility(){
  const hasConversation=chatBox.querySelectorAll(".message").length>1;
  if(welcomeBlock) welcomeBlock.hidden=hasConversation;
  if(suggestions) suggestions.hidden=hasConversation;
}
function addMessage(message,sender,source=null,stamp=""){
  const row=document.createElement("div");
  row.className=`message ${sender==="user"?"user-message":"bot-message"}`;
  const avatar=document.createElement("div");
  avatar.className="message-avatar";
  avatar.textContent=sender==="user"?"U":"✚";
  const content=document.createElement("div");
  content.className="message-content";
  const name=document.createElement("span");
  name.className="sender";
  name.textContent=sender==="user"?"You":"CareBridge AI";
  if(stamp){const time=document.createElement("time");time.textContent=stamp;name.append(" ",time);}
  const bubble=document.createElement("div");
  bubble.className="bubble";
  bubble.textContent=String(message??"");
  content.append(name,bubble);
  if(sender==="bot"&&source?.url){
    try{
      const parsed=new URL(source.url,window.location.origin);
      if(["https:","http:"].includes(parsed.protocol)){
        const link=document.createElement("a");
        link.href=parsed.href;link.textContent=`Source: ${source.name||"Read more"}`;
        link.target="_blank";link.rel="noopener noreferrer";content.append(link);
      }
    }catch(e){console.warn("Invalid source URL",e);}
  }
  row.append(avatar,content);chatBox.append(row);
  chatBox.scrollTop=chatBox.scrollHeight;updateIntroVisibility();
}
function showTyping(){typingIndicator.hidden=false;}
function hideTyping(){typingIndicator.hidden=true;}
async function sendMessage(message){
  const clean=String(message||"").trim();
  if(!clean||sendButton.disabled)return;
  addMessage(clean,"user");
  userInput.value="";sendButton.disabled=true;userInput.disabled=true;showTyping();
  try{
    const response=await fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:clean})});
    const data=await response.json();
    if(!response.ok||data.status!=="success")throw new Error(data.message||`Server error (${response.status})`);
    addMessage(data.response,"bot",{name:data.source_name,url:data.source_url});
    await loadHistory();
  }catch(error){
    console.error("Chat request failed:",error);
    addMessage("I couldn't connect to the server. Please check that the Flask application is running, then try again.","bot");
  }finally{hideTyping();sendButton.disabled=false;userInput.disabled=false;userInput.focus();}
}
chatForm.addEventListener("submit",e=>{e.preventDefault();sendMessage(userInput.value);});
document.querySelectorAll("[data-question]").forEach(button=>button.addEventListener("click",()=>sendMessage(button.dataset.question)));

function formatTime(value){
  if(!value)return "";
  const date=new Date(value);
  return Number.isNaN(date.getTime())?"":date.toLocaleString([], {month:"short",day:"numeric",hour:"2-digit",minute:"2-digit"});
}
async function loadHistory(restoreLatest=false){
  try{
    const response=await fetch("/api/history");
    if(!response.ok)throw new Error("Could not load history");
    const data=await response.json();
    const history=Array.isArray(data.history)?data.history:[];
    historyCount.textContent=String(history.length);
    historyList.replaceChildren();
    if(!history.length){
      const empty=document.createElement("p");empty.className="history-empty";empty.textContent="Your recent questions will appear here.";historyList.append(empty);return;
    }
    if(restoreLatest && history.length){
      chatBox.replaceChildren();
      history.slice(-10).forEach(item=>{
        addMessage(item.user_message,"user",null,formatTime(item.created_at));
        addMessage(item.bot_response,"bot",null,formatTime(item.created_at));
      });
    }
    history.slice().reverse().slice(0,12).forEach(item=>{
      const button=document.createElement("button");button.type="button";button.className="history-item";
      button.textContent=item.user_message||"Previous question";
      button.title=item.user_message||"";
      button.addEventListener("click",()=>{
        chatBox.replaceChildren();
        addMessage(item.user_message,"user",null,formatTime(item.created_at));
        addMessage(item.bot_response,"bot",null,formatTime(item.created_at));
        userInput.focus();
      });
      historyList.append(button);
    });
  }catch(error){console.warn("History unavailable:",error);}
}
document.getElementById("newChat").addEventListener("click",()=>{
  chatBox.replaceChildren();
  addMessage("Hello! Welcome. You can ask me general questions about healthcare, nutrition, fitness and wellness. What would you like to know today?","bot");
  userInput.value="";updateIntroVisibility();userInput.focus();
  document.getElementById("sidebar").classList.remove("open");
});
document.getElementById("homeLink").addEventListener("click",()=>{
  chatBox.replaceChildren();
  addMessage("Hello! Welcome. You can ask me general questions about healthcare, nutrition, fitness and wellness. What would you like to know today?","bot");
  updateIntroVisibility();
});
clearButton.addEventListener("click",async()=>{
  if(!confirm("This will permanently delete all saved chat history. Continue?"))return;
  clearButton.disabled=true;
  try{
    const response=await fetch("/api/history/clear",{method:"DELETE"});
    const data=await response.json();
    if(!response.ok||data.status!=="success")throw new Error(data.message||"Unable to clear history");
    chatBox.replaceChildren();
    addMessage("Your saved conversation history has been cleared. How can I help you today?","bot");
    await loadHistory();
  }catch(error){alert("Could not clear saved history. Please try again.");console.error(error);}
  finally{clearButton.disabled=false;}
});
document.getElementById("menuToggle").addEventListener("click",()=>document.getElementById("sidebar").classList.toggle("open"));
document.addEventListener("click",e=>{
  const sidebar=document.getElementById("sidebar");
  if(window.innerWidth<=700&&!sidebar.contains(e.target)&&!e.target.closest("#menuToggle"))sidebar.classList.remove("open");
});
loadHistory(true);
