import { Events } from "./events"
import {twitchChannelUrlValidator, youtubeChannelUrlValidator} from "./validators"

export interface IPriceCategory {
    id: number
    name: string
}

export interface IMinMaxStep {
    min: number
    max: number
    step: number
}

export interface IPrice {
    id: number
    name: string
    category: number
    price: number
    views: IMinMaxStep
    viewers: IMinMaxStep
    description: string
}

export interface ISmoothGain {
    enabled: boolean
    minutes: number

}

export interface ITask {
    expires_at: string
    id: string
    url: string
}

export interface ITaskStatus {
    status: "pending" | "in_progress" | "completed" | "action_required" | "error"
}

export interface IOrder {
    errors: string[]
    platform: string
    categories: IPriceCategory[]
    category_id: number;
    prices: IPrice[]
    price_id: number
    number_of_views: number
    number_of_viewers: number
    launch_mode: "auto" | "manual" | "delay"
    smooth_gain: ISmoothGain
    delay_time: number
    channel_url: string
    twitch_id: number

    isValid: () => boolean;
    build: () => Map<string, any>
    toJson: () => string
}

export class SmoothGain implements ISmoothGain{
    enabled: boolean = false;
    minutes: number = 0;
}

export class Order implements IOrder {
    errors: string[] = []
    platform: string
    categories: IPriceCategory[]
    category_id: number
    prices: IPrice[]
    price_id: number
    number_of_viewers: number
    number_of_views: number
    launch_mode: "auto" | "manual" | "delay"
    smooth_gain: ISmoothGain
    delay_time: number
    channel_url: string
    twitch_id: number

    constructor() {
            this.platform = ""
            this.categories = []
            this.category_id = 0
            this.prices = []
            this.price_id = 0
            this.number_of_viewers = 0
            this.number_of_views = 0
            this.launch_mode = "auto"
            this.smooth_gain = new SmoothGain()
            this.delay_time = 0
            this.channel_url = ""
            this.twitch_id = 0

            const form = document.getElementById("newOrderForm")
            if (form) {
                if(form.dataset.platform)
                    this.platform = form.dataset.platform

                if(form.dataset.categories)
                    this.categories = JSON.parse(atob(form.dataset.categories))

                if(form.dataset.prices)
                    this.prices = JSON.parse(atob(form.dataset.prices))
            }
    }

    isValid(): boolean {
        this.errors = [];

        switch(this.platform){
            case "twitch":
                if (!twitchChannelUrlValidator(this.twitch_id))
                    this.errors.push("Invalid Twitch Channel ID")
                break
            case "youtube":
                if (this.channel_url == "")
                    this.errors.push("Channel information not specified")

                if (!youtubeChannelUrlValidator(this.channel_url))
                    this.errors.push("Invalid YouTube Channel URL")
                break
            default:
                this.errors.push("Invalid Platform code")
        }

        if (this.price_id <= 0)
            this.errors.push("Invalid Price Id: Value must be greater than zero");

        if (this.number_of_viewers <= 0)
            this.errors.push("The minimum number of spectators must be at least ten");

        if (this.number_of_views <= 0)
            this.errors.push("The number of views must be at least a thousand");

        if (this.launch_mode == "delay") {
            if (this.delay_time <= 0)
                this.errors.push("If delayed start of an order is selected, then the delayed start time must be at least one minute")
        }

        return !this.errors.length;
    }

    build(): Map<string, any> {
        let m = new Map<string, any>()
        m.set("price_id", this.price_id)
        m.set("number_of_viewers", this.number_of_viewers)
        m.set("number_of_views", this.number_of_views)
        m.set("launch_mode", this.launch_mode)
        m.set("smooth_gain", this.smooth_gain)
        m.set("delay_time", this.delay_time)
        switch (this.platform) {
            case "twitch":
                m.set("twitch_id", this.twitch_id)
                break
            case "youtube":
                m.set("channel_url", this.channel_url)
                break
        }

        return m;
    }

    toJson(): string {
        const o = Object.fromEntries(this.build());
        return JSON.stringify(o);
    }
}
