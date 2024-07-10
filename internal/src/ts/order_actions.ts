import { Events } from "./events"

export const orderActions = () => {
    const viewers = <HTMLInputElement>document.getElementById("orderDetailViewers"),
        launch = <HTMLSelectElement>document.getElementById("orderDetailLaunchMode"),
        smoothGain = <HTMLInputElement>document.getElementById("orderDetailSmoothGain"),
        smoothPeriod = <HTMLInputElement>document.getElementById("orderDetailSmoothPeriod"),
        delayPeriod = <HTMLInputElement>document.getElementById("orderDetailDelayLaunchPeriod"),
        addViews = <HTMLInputElement>document.getElementById("orderDetailAddViews"),
        addViewsTmp = <HTMLElement>document.getElementById("addViewsTmp"),
        action = <HTMLButtonElement>document.getElementById("orderDetailAction"),
        cancel = <HTMLButtonElement>document.getElementById("orderDetailCancel"),
        csrfmiddlewaretoken = <HTMLInputElement>document.querySelector(`input[name="csrfmiddlewaretoken"]`)

    if (csrfmiddlewaretoken == null) {
        console.error("csrfmiddlewaretoken is null")
        return
    }

    if (viewers) {
        viewers.onchange = () =>{
            const value = parseInt(viewers.value)
            window.dispatchEvent(new CustomEvent(Events.ChangeOnlineValue, {
                detail: {
                    value: isNaN(value) ? 0 : value,
                    csrfmiddlewaretoken: csrfmiddlewaretoken.value
                }
            }))
        }
    }

    if (smoothGain) {
        smoothGain.onchange = () => {
            if (smoothGain.checked) {
                window.dispatchEvent(new CustomEvent(Events.IncreaseOn, {
                    detail: {
                        csrfmiddlewaretoken: csrfmiddlewaretoken.value
                    }
                }))
            } else {
                window.dispatchEvent(new CustomEvent(Events.IncreaseOff, {
                    detail: {
                        csrfmiddlewaretoken: csrfmiddlewaretoken.value
                    }
                }))
            }
        }
    }

    if (launch) {
        launch.onchange = () => {
            window.dispatchEvent(new CustomEvent(Events.ChangeLaunchMode, {
                detail: {
                    value: launch.value,
                    csrfmiddlewaretoken: csrfmiddlewaretoken.value
                }
            }))
        }
    }

    if (smoothPeriod) {
        smoothPeriod.onchange = () => {
            const value = parseInt(smoothPeriod.value)
            window.dispatchEvent(new CustomEvent(Events.ChangeIncreaseValue, {
                detail: {
                    value: isNaN(value) ? 0 : value,
                    csrfmiddlewaretoken: csrfmiddlewaretoken.value
                }
            }))
        }
    }

    if (delayPeriod) {
        delayPeriod.onchange = () => {
            const value = parseInt(delayPeriod.value)
            window.dispatchEvent(new CustomEvent(Events.ChangeDelayTime, {
                detail: {
                    value: isNaN(value) ? 0 : value,
                    csrfmiddlewaretoken: csrfmiddlewaretoken.value
                }
            }))
        }
    }

    if (addViews) {
        if (addViewsTmp) {
            addViews.onkeyup = () => {
                const value = parseInt(addViews.value),
                    price = addViewsTmp.dataset.price
                if (isNaN(value) || value < 1) {
                    addViewsTmp.textContent = "0"
                } else {
                    if (price) {
                        addViewsTmp.textContent = (value * parseFloat(price)).toFixed(2).toString()
                    } else {
                        addViewsTmp.textContent = "0"
                    }
                }
            }
        }

        addViews.onchange = () => {
            const value = parseInt(addViews.value)
            window.dispatchEvent(new CustomEvent(Events.AddViews, {
                detail: {
                    value: isNaN(value) ? 0 : value,
                    csrfmiddlewaretoken: csrfmiddlewaretoken.value
                }
            }))
        }
    }

    if (action) {
        action.onclick = () => {
            const a = action.dataset.action
            if (a) {
                if (a == "pay")
                    console.log("pay")
                
                if (a == "run") {
                    window.dispatchEvent(new CustomEvent(Events.Run, {
                        detail: {
                            csrfmiddlewaretoken: csrfmiddlewaretoken.value
                        }
                    }))
                }

                if (a == "stop") {
                    window.dispatchEvent(new CustomEvent(Events.Stop, {
                        detail: {
                            csrfmiddlewaretoken: csrfmiddlewaretoken.value
                        }
                    }))
                }
            }
        }
    }

    if (cancel) {
        cancel.onclick = () => {
            window.dispatchEvent(new CustomEvent(Events.Cancel, {
                detail: {
                    csrfmiddlewaretoken: csrfmiddlewaretoken.value
                }
            }))
        }
    }
}
