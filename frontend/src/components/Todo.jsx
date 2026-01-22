import React, { useEffect, useRef, useState } from 'react'
import todo_icon from '../assets/todo_icon.png'
import TodoItems from './TodoItems'

const Todo = () => {

// const [todoList, setTodoList] = useState(localStorage.getItem("todos") ? JSON.parse(localStorage.getItem("todos")) : []);

const [todoList, setTodoList] = useState([]);

const inputRef = useRef();

const add = () => {
    const inputText = inputRef.current.value.trim();

    if(inputText === ""){
        return null;
    }
    
    const newTodo = {
        id: Date.now(),
        text: inputText,
        isComplete: false,
    }
    console.log(newTodo);
    fetch("http://localhost:8000/tasks", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            id: newTodo.id,
            title: inputText,
        }),
    }).then((response) => console.log(response));

    setTodoList((prev)=> [...prev, newTodo]);
    inputRef.current.value = "";
}

const deleteTodo = (id) =>{
    setTodoList((prvTodos)=>{
        fetch(`http://localhost:8000/tasks/${id}`, {
            method: "DELETE",
        }).then((response) => console.log(response));
        return prvTodos.filter((todo) => todo.id !== id)
    })
}

const toggle = (id) =>{
    setTodoList((prevTodos)=>{
        return prevTodos.map((todo)=>{
            if(todo.id === id){
                fetch(`http://localhost:8000/tasks/${id}`, {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        title: todo.text,
                        is_complete: !todo.isComplete
                    }),
                }).then((response) => console.log(response));
                return {...todo, isComplete: !todo.isComplete}
            }
            return todo;
        })
    })
}

// useEffect(()=>{
//     //localStorage.setItem("todos", JSON.stringify(todoList))
// }, [todoList])

async function getTask(){
    try{
        const response = await fetch('http://localhost:8000/tasks');

        const data = await response.json();

        for(var i = 0;i<data.length;i++){
            const newTodo = {
                id: data[i].id,
                text: data[i].title,
                isComplete: data[i].is_complete,
            }
            setTodoList((prev)=> [...prev, newTodo]);
        }
    }
    catch(error){
        console.error('error', error);
    }
}
useEffect(() =>{
    getTask();
}, [])

  return (
    
    <div className='bg-white place-self-center w-11/12 max-w-md flex flex-col p-7 min-h-[550px] rounded-xl'>
      
{/* --------- title ------------ */}

    <div className='flex items-center mt-7 gap-2'>
        <img className='w-8' src={todo_icon} alt="" />
        <h1 className='text-3xl font-semibold'>To-Do List</h1>
    </div>

{/* --------- input box ------------ */}

    <div className='flex items-center my-7 bg-gray-200 rounded-full'>
        <input ref={inputRef} className='bg-transparent border-0 outline-none flex-1 h-14 pl-6 pr-2 placeholder:text-slate-600' type="text" placeholder='Add your task'/>
        <button onClick={add} className='border-none rounded-full bg-orange-600 w-32 h-14 text-white text-lg font-medium cursor-pointer'>ADD +</button>
    </div>

{/* --------- todo list ------------ */}

    <div>
        {todoList.map((item, index)=> {
            return <TodoItems key={index} text={item.text} id={item.id}
            isComplete={item.isComplete} deleteTodo={deleteTodo}
            toggle={toggle}/>
        })}
    </div>

    </div>
  )
}

export default Todo
