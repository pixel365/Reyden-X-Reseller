import {Events} from "./events"
import {Order} from "./model"

export const newOrder = () => {
    (<any>window).new_order = new Order();
    window.dispatchEvent(new CustomEvent(Events.OrderInitiated));

    const submitBtn = document.getElementById("createNewOrder"),
        tariffSelect = <HTMLSelectElement>document.getElementById("tariffSelect"),
        viewers = <HTMLInputElement>document.getElementById("viewers"),
        views = <HTMLInputElement>document.getElementById("views"),
        smoothGain = <HTMLInputElement>document.getElementById("smoothGain"),
        smoothPeriod = <HTMLInputElement>document.getElementById("smoothPeriod"),
        launch = <HTMLSelectElement>document.getElementById("launch"),
        delayLaunchPeriod = <HTMLInputElement>document.getElementById("delayLaunchPeriod"),
        channelInfo = <HTMLInputElement>document.getElementById("channelInfo")

    if (submitBtn && tariffSelect && viewers && views && smoothGain && smoothPeriod 
            && launch && delayLaunchPeriod) {
        submitBtn.onclick = (ev: MouseEvent) => {
            ev.preventDefault()
            window.dispatchEvent(new Event(Events.SubmitOrder))
        }

        tariffSelect.onchange = () => {
            window.dispatchEvent(new CustomEvent(Events.ChangeTariff, {
                detail: {
                    id: parseInt(tariffSelect.value)
                }
            }))
        }

        viewers.onchange = () => {
            window.dispatchEvent(new Event(Events.ChangeViewers))
        }

        views.onchange = () => {
            window.dispatchEvent(new Event(Events.ChangeViews))
        }

        smoothGain.onchange = () => {
            window.dispatchEvent(new CustomEvent(Events.ChangeSmoothGain, {
                detail: {
                    checked: smoothGain.checked
                }
            }))
        }

        smoothPeriod.onchange = () => {
            window.dispatchEvent(new CustomEvent(Events.ChangeSmoothGain, {
                detail: {
                    checked: smoothGain.checked
                }
            }))
        }

        launch.onchange = () => {
            window.dispatchEvent(new CustomEvent(Events.ChangeLaunchParams, {
                detail: {
                    value: launch.value
                }
            }))
        }

        delayLaunchPeriod.onchange = () => {
            window.dispatchEvent(new CustomEvent(Events.ChangeLaunchParams, {
                detail: {
                    value: launch.value
                }
            }))
        }

        channelInfo.onchange = () => {
            window.dispatchEvent(new CustomEvent(Events.ChangeUrl, {
                detail: {
                    value: channelInfo.value
                }
            }))
        }
    }
}
