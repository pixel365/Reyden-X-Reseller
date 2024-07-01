import {Events} from "./events"
import {Order, IPriceCategory, IPrice, ITask, ITaskStatus} from "./model"
import * as toastr from "toastr"

toastr.options.closeButton = true
toastr.options.tapToDismiss = true
toastr.options.escapeHtml = false

const opRequest = (action: "run" | "cancel" | "stop" | "increase_off", csrfmiddlewaretoken: string): boolean => {
    let success = false
    const headers = new Headers(),
        m = new Map<string, string>()
    headers.append("X-CSRFToken", csrfmiddlewaretoken)
    m.set("action", action)

    fetch(window.location.pathname, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(Object.fromEntries(m))
    }).then(response => {
        success = response.ok
        if (success) {
            response.json().then((data: ITask) => {
                toastr.success(`Change request completed successfully!<br />Task Id: ${data.id}<br /><a href="${data.url}" target="_blank">Click to check execution status</a>`)
            })
        }
    }).catch(e => {
        console.error(e)
        toastr.error("Failure to accept change request")
    }).finally(() => {
    })

    return success
}

const changeRequest = (el: HTMLInputElement, action: string, value: number, csrfmiddlewaretoken: string): boolean => {
    let success = false
    el.disabled = true
    el.classList.add("readonly-input")

    const headers = new Headers(),
        m = new Map<string, string|number>()
    headers.append("X-CSRFToken", csrfmiddlewaretoken)
    m.set("action", action)
    m.set("value", value)

    fetch(window.location.pathname, {
        method: "POST",
        headers: headers,
        body: JSON.stringify(Object.fromEntries(m))
    }).then(response => {
        success = response.ok
        if (success) {
            response.json().then((data: ITask) => {
                toastr.success(`Change request completed successfully!<br />Task Id: ${data.id}<br /><a href="${data.url}" target="_blank">Click to check execution status</a>`)
            })
        }
    }).catch(e => {
        console.error(e)
        toastr.error("Failure to accept change request")
    }).finally(() => {
        el.disabled = false
        el.classList.remove("readonly-input")
    })

    return success
}

export const eventListeners = () => {
    window.addEventListener(Events.OrderInitiated, () => {
        const newOrder = (<any>window).new_order
        if(newOrder instanceof Order) {
            const priceCategories = document.getElementById("priceCategories")
            if (priceCategories) {
                let i: number = 0, checked: string = ""
                newOrder.categories.forEach((item: IPriceCategory) => {
                    i++;
                    if (i < 2){
                        checked = " checked"
                        newOrder.category_id = item.id
                    }else{
                        checked = ""
                    }

                    priceCategories.innerHTML += `<div class="col-md">
                            <div class="form-check custom-option custom-option-basic${checked}" 
                                id="category-wrapper-${item.id}">
                                <label class="form-check-label custom-option-content" for="category-${item.id}">
                                    <input class="form-check-input dynamic-category" type="radio" 
                                        value="${item.id}" name="category"
                                        id="category-${item.id}"${checked}>
                                    <span class="custom-option-header">
                                        <span class="h6 mb-0">${item.name}</span>
                                    </span>
                                </label>
                            </div>
                        </div>`
                })

                window.dispatchEvent(new CustomEvent(Events.ChangeTariff, {
                    detail: {
                        id: 0
                    }
                }))

                const categories: NodeListOf<HTMLInputElement> = document.querySelectorAll("input.dynamic-category")
                categories.forEach((item) => {
                    item.onchange = () => {
                        newOrder.category_id = parseInt(item.value)
                        window.dispatchEvent(new CustomEvent(Events.ChangeTariff,{
                            detail: {
                                id: 0
                            }
                        }))
                    }
                })
            }
        }
    })

    window.addEventListener(Events.ChangeTariff, ((ev: CustomEvent) => {
        const newOrder = (<any>window).new_order
        if (newOrder instanceof Order) {
            newOrder.categories.forEach((item) => {
                const wr = document.getElementById(`category-wrapper-${item.id}`),
                    inp = document.querySelector<HTMLElement>(`input[type="radio"]#category-${item.id}`);
                if (wr && inp) {
                    if(newOrder.category_id == item.id) {
                        wr.classList.add("checked")
                        inp.setAttribute("checked", "")
                    } else {
                        wr.classList.remove("checked")
                        inp.removeAttribute("checked")
                    }
                }
            })

            const tariffSelect = document.getElementById("tariffSelect")
            if (tariffSelect) {
                tariffSelect.innerHTML = ""
                let i: number = 0, selected: string = ""
                newOrder.prices.forEach((item: IPrice) => {
                    if (item.category == newOrder.category_id) {
                        i++
                        if (ev.detail.id == 0 && i == 1) {
                            newOrder.price_id = item.id
                        } else {
                            if (item.id == ev.detail.id) {
                                newOrder.price_id = item.id
                                selected = " selected"
                            } else {
                                selected = ""
                            }
                        }
                        tariffSelect.innerHTML += `<option value="${item.id}"${selected}>${item.name} (${item.description})</option>`
                    }
                })

                window.dispatchEvent(new Event(Events.ChangeViewers))
                window.dispatchEvent(new Event(Events.ChangeViews))
            }
        }
    }) as EventListener)

    window.addEventListener(Events.ChangeViewers, () => {
        const newOrder = (<any>window).new_order
        if (newOrder instanceof Order) {
            const price = newOrder.prices.filter((item) => item.id == newOrder.price_id)
            const viewers = <HTMLInputElement>document.getElementById("viewers")
            if (price.length == 1 && viewers) {
                let value = parseInt(viewers.value)
                if (isNaN(value)) {
                    value = price[0].viewers.min
                    viewers.value = value.toString()
                }

                if (value < price[0].viewers.min){
                    viewers.value = price[0].viewers.min.toString()
                }

                if (value > price[0].viewers.max){
                    viewers.value = price[0].viewers.max.toString()
                }

                newOrder.number_of_viewers = parseInt(viewers.value)
            }

            window.dispatchEvent(new Event(Events.Calculate))
        }
    })

    window.addEventListener(Events.ChangeViews, () => {
        const newOrder = (<any>window).new_order
        if (newOrder instanceof Order) {
            const price = newOrder.prices.filter((item) => item.id == newOrder.price_id)
            const views = <HTMLInputElement>document.getElementById("views")
            if (price.length == 1 && views) {
                let value = parseInt(views.value)
                if (isNaN(value)) {
                    value = price[0].views.min
                    views.value = value.toString()
                }

                if (value < price[0].views.min) {
                    views.value = price[0].views.min.toString()
                }

                if (value > price[0].views.max) {
                    views.value = price[0].views.max.toString()
                }

                newOrder.number_of_views = parseInt(views.value)
            }

            window.dispatchEvent(new Event(Events.Calculate))
        }
    })

    window.addEventListener(Events.ChangeSmoothGain, ((ev: CustomEvent) => {
        const newOrder = (<any>window).new_order
        if (newOrder instanceof Order) {
            const smoothPeriodArea = document.getElementById("smoothPeriodArea"),
                smoothPeriod = <HTMLInputElement>document.getElementById("smoothPeriod")
            if (smoothPeriodArea && smoothPeriod) {
                newOrder.smooth_gain.enabled = ev.detail.checked
                if (ev.detail.checked) {
                    smoothPeriodArea.style.display = ""
                    let minutes = parseInt(smoothPeriod.value)
                    if (isNaN(minutes)) {
                        minutes = 10
                        smoothPeriod.value = minutes.toString()
                    }
                    newOrder.smooth_gain.minutes = minutes

                    if (minutes < 10)
                        newOrder.smooth_gain.minutes = 10

                    if (minutes > 240)
                        newOrder.smooth_gain.minutes = 240
                } else {
                    newOrder.smooth_gain.minutes = 0
                    smoothPeriodArea.style.display = "none"
                }
            }
        }
    }) as EventListener)

    window.addEventListener(Events.ChangeLaunchParams, ((ev: CustomEvent) => {
        const newOrder = (<any>window).new_order
        if (newOrder instanceof Order) {
            const delayLaunchArea = document.getElementById("delayLaunchArea"),
                delayLaunchPeriod = <HTMLInputElement>document.getElementById("delayLaunchPeriod")
            if (delayLaunchArea && delayLaunchPeriod) {
                newOrder.launch_mode = ev.detail.value
                if (ev.detail.value == "delay") {
                    delayLaunchArea.style.display = ""
                    let minutes = parseInt(delayLaunchPeriod.value)
                    if (isNaN(minutes)) {
                        minutes = 10
                        delayLaunchPeriod.value = minutes.toString()
                    }

                    newOrder.delay_time = minutes
                    if (minutes < 0)
                        newOrder.delay_time = 1

                    if (minutes > 240)
                        newOrder.delay_time = 240
                } else {
                    delayLaunchArea.style.display = "none"
                    newOrder.delay_time = 0
                }
            }
        }
    }) as EventListener)

    window.addEventListener(Events.Calculate, () => {
        const newOrder = (<any>window).new_order
        if (newOrder instanceof Order) {
            const price = newOrder.prices.filter((item) => item.id == newOrder.price_id)
            const views = <HTMLInputElement>document.getElementById("views"),
                total = document.getElementById("total")
            if (price.length == 1 && views && total) {
                let value = parseInt(views.value)
                if (isNaN(value)) {
                    value = price[0].views.min
                    views.value = value.toString()
                }

                total.innerText = (price[0].price * value).toFixed(2).toString()
            }
        }
    })

    window.addEventListener(Events.ChangeUrl, ((ev: CustomEvent) => {
        const newOrder = (<any>window).new_order
        if (newOrder instanceof Order) {
            switch (newOrder.platform) {
                case "twitch":
                    newOrder.twitch_id = parseInt(ev.detail.value)
                    break
                case "youtube":
                    newOrder.channel_url = ev.detail.value.toString()
                    break
            }
        }
    }) as EventListener)

    window.addEventListener(Events.SubmitOrder, () => {
        const newOrder = (<any>window).new_order
        if (newOrder instanceof Order) {
            const errors = document.getElementById("errors")
            if (errors) {
                errors.innerHTML = ""
                if (newOrder.isValid()) {
                    const form = <HTMLFormElement>document.getElementById("newOrderForm")
                    if (form && form.dataset.csrf) {
                        const headers = new Headers()
                        headers.append("X-CSRFToken", form.dataset.csrf)

                        fetch(form.action, {
                            method: "POST",
                            headers: headers,
                            body: newOrder.toJson()
                        }).then(response => {
                            if (response.ok) {
                                response.json().then((data: ITask) => {
                                    const removable = document.querySelectorAll(".removable")
                                    if (removable) {
                                        removable.forEach(item => {
                                            item.remove()
                                        })
                                    }

                                    window.dispatchEvent(new CustomEvent<ITask>(Events.WatchTask, {
                                        detail: data
                                    }))
                                })
                            }
                        }).catch(error => {
                            console.log(error)
                        })
                    }
                } else {
                    newOrder.errors.forEach(error => {
                        errors.innerHTML += `<div class="alert alert-danger" role="alert">${error}</div>`
                    })
                }
            }
        }
    })

    window.addEventListener(Events.WatchTask, ((ev: CustomEvent) => {
        const task: ITask = ev.detail
        const taskProgress = document.getElementById("taskProgress"),
            shown = document.querySelectorAll<HTMLElement>(".shown"),
            loader = document.getElementById("loader")
        if (taskProgress && shown && loader) {
            shown.forEach(item => {
                item.style.display = ""
            })
            const id = setInterval(() => {
                fetch(task.url, {
                    method: "GET",
                    cache: "no-cache"
                }).then(response => {
                    if (response.ok) {
                        response.json().then((data: ITaskStatus) => {
                            const m = `Task: ${task.id}<br />URL: <a href="${task.url}" target="_blank">${task.url}</a>`
                            switch (data.status) {
                                case "pending":
                                    taskProgress.innerHTML += `<div class="alert alert-info" role="alert">${m}<br />Status: Pending</div>`
                                    break
                                case "in_progress":
                                    taskProgress.innerHTML += `<div class="alert alert-secondary" role="alert">${m}<br />Status: In Progress</div>`
                                    break
                                case "completed":
                                    taskProgress.innerHTML += `<div class="alert alert-success" role="alert">${m}<br />Status: Completed</div>`
                                    clearInterval(id)
                                    loader.remove()
                                    break
                                case "action_required":
                                    taskProgress.innerHTML += `<div class="alert alert-warning" role="alert">${m}<br />Status: Action Required</div>`
                                    clearInterval(id)
                                    loader.remove()
                                    break
                                case "error":
                                    taskProgress.innerHTML += `<div class="alert alert-danger" role="alert">${m}<br />Status: Error</div>`
                                    clearInterval(id)
                                    loader.remove()
                                    break
                            }
                        })
                    }
                }).catch(() => {
                })
            }, 2000)
        }
    }) as EventListener)

    window.addEventListener(Events.Run, ((ev: CustomEvent) => {
        opRequest("run", ev.detail.csrfmiddlewaretoken)
    }) as EventListener)

    window.addEventListener(Events.Stop, ((ev: CustomEvent) => {
        opRequest("stop", ev.detail.csrfmiddlewaretoken)
    }) as EventListener)

    window.addEventListener(Events.Cancel, (ev: any) => {
        opRequest("cancel", ev.detail.csrfmiddlewaretoken)
    })

    window.addEventListener(Events.IncreaseOff, ((ev: CustomEvent) => {
        const smoothPeriodArea = document.getElementById("orderDetailSmoothPeriodArea"),
            smoothPeriod = <HTMLInputElement>document.getElementById("orderDetailSmoothPeriod")
        if (smoothPeriodArea && smoothPeriod) {
            smoothPeriodArea.style.display = "none"
            smoothPeriod.value = "0"
            opRequest("increase_off", ev.detail.csrfmiddlewaretoken)
        }
    }) as EventListener)

    window.addEventListener(Events.IncreaseOn, ((ev: CustomEvent) => {
        const smoothPeriodArea = document.getElementById("orderDetailSmoothPeriodArea"),
            smoothPeriod = <HTMLInputElement>document.getElementById("orderDetailSmoothPeriod")
        if (smoothPeriodArea && smoothPeriod) {
            smoothPeriodArea.style.display = ""
            let minutes = parseInt(smoothPeriod.value)
            if (isNaN(minutes)) {
                minutes = 10
                smoothPeriod.value = minutes.toString()
            }

            if (minutes > 0) {
                changeRequest(smoothPeriod, Events.IncreaseOn, minutes, ev.detail.csrfmiddlewaretoken)
            }
        }
    }) as EventListener)

    window.addEventListener(Events.ChangeOnlineValue, ((ev: CustomEvent) => {
        if (ev.detail.value > 0) {
            const el = <HTMLInputElement>document.getElementById("orderDetailViewers")
            if (el) {
                changeRequest(el, Events.ChangeOnlineValue, ev.detail.value, ev.detail.csrfmiddlewaretoken)
            }
        }
    }) as EventListener)

    window.addEventListener(Events.ChangeIncreaseValue, ((ev: CustomEvent) => {
        if (ev.detail.value > 0) {
            const el = <HTMLInputElement>document.getElementById("orderDetailSmoothPeriod")
            if (el) {
                changeRequest(el, Events.ChangeIncreaseValue, ev.detail.value, ev.detail.csrfmiddlewaretoken)
            }
        }
    }) as EventListener)

    window.addEventListener(Events.AddViews, ((ev: CustomEvent) => {
        if (ev.detail.value > 0) {
            const el = <HTMLInputElement>document.getElementById("orderDetailAddViews")
            if (el) {
                const success = changeRequest(el, Events.AddViews, ev.detail.value, ev.detail.csrfmiddlewaretoken)
                if (success) {
                    //todo
                }
            }
        }
    }) as EventListener)

    window.addEventListener(Events.ChangeLaunchMode, ((ev: CustomEvent) => {
        const delayLaunchArea = document.getElementById("orderDetailDelayLaunchArea"),
             delayLaunchPeriod = <HTMLInputElement>document.getElementById("orderDetailDelayLaunchPeriod")
            if (delayLaunchArea && delayLaunchPeriod) {
                const mode = ev.detail.value
                console.log("ChangeLaunchMode", mode)
                if (mode == "delay") {
                    delayLaunchArea.style.display = ""
                    let minutes = parseInt(delayLaunchPeriod.value)
                    if (isNaN(minutes))
                        minutes = 10

                    if (minutes <= 0)
                        minutes = 1

                    if (minutes > 240)
                        minutes = 240

                    delayLaunchPeriod.value = minutes.toString()
                } else {
                    delayLaunchArea.style.display = "none"

                    switch (mode) {
                        case "auto":
                        case "manual":
                            break
                    }
                }
            }
    }) as EventListener)

    window.addEventListener(Events.ChangeDelayPeriod, ((ev: CustomEvent) => {
        if (ev.detail.value > 0) {
            //todo: change node to 'delay'
            console.log("ChangeDelayPeriod", ev.detail.value)
        }
    }) as EventListener)
}
