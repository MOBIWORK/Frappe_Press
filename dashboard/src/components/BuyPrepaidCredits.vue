<template>
	<div>
		<FormControl
			v-if="step == 'Create order'"
			class="mb-2"
			label="Số tiền"
			v-model.number="creditsToBuy"
			name="amount"
			autocomplete="off"
			type="number"
			:min="minimumAmount"
		/>
		<!-- <label
      class="block"
      :class="{
        'h-0.5 opacity-0': step != 'Add Card Details',
        'mt-4': step == 'Add Card Details'
      }"
    >
      <span class="text-sm leading-4 text-gray-700">
        Thẻ Tín dụng hoặc Thẻ Ghi nợ
      </span>
      <div
        class="form-input mt-2 block w-full py-2 pl-3"
        ref="card-element"
      ></div>
      <ErrorMessage class="mt-1" :message="cardErrorMessage" />
    </label> -->

		<FormControl
			v-if="step == 'Create order'"
			label=""
			disabled
			hidden
			v-model="total"
			name="total"
			autocomplete="off"
			type="number"
		/>
		<div v-if="step == 'Create order'" class="mt-2 text-base">
			<table class="table-auto text-sm">
				<tbody>
					<tr>
						<th>Số dư tài khoản:</th>
						<td class="pl-2">+ {{ this.$formatMoney(total) }} VND</td>
					</tr>
					<tr v-if="depositBonus">
						<th>Số dư khuyến mại 2:</th>
						<td class="pl-2">+ {{ this.$formatMoney(depositBonus) }} VND</td>
					</tr>
				</tbody>
			</table>
			<div class="my-4" v-if="textDepositBonus">{{ textDepositBonus }}</div>
		</div>

		<!-- <div v-if="step == 'Setting up Stripe'" class="mt-8 flex justify-center">
			<Spinner class="h-4 w-4 text-gray-600" />
		</div> -->
		<ErrorMessage
			class="mt-2"
			:message="
				(['1', '2'].includes($resources.createaOrder.data?.code) &&
					$resources.createaOrder.data?.desc) ||
				errorMessage
			"
		/>
		<router-link
			v-if="$resources.createaOrder.data?.code == 1"
			class="text-sm underline"
			to="credit-balance"
		>
			Đến thanh toán
		</router-link>
		<div v-if="infoOrder">
			<div>Thông tin hóa đơn đã được tạo:</div>
			<div class="rounded-md border p-2">
				<p>Mã hóa đơn: {{ infoOrder.order_code }}</p>
				<p>Số tiền: {{ formatAmount() }} VND</p>
				<p>Nội dung: {{ infoOrder.description }}</p>
			</div>
		</div>

		<div class="mt-4 flex w-full justify-between">
			<!-- <StripeLogo /> -->
			<PayOSLogo />
			<div v-if="step == 'Create order'">
				<Button
					variant="solid"
					@click="$resources.createaOrder.submit()"
					:loading="$resources.createaOrder.loading"
				>
					Tạo hóa đơn
				</Button>
			</div>
			<div v-if="step == 'Get link payment'">
				<Button @click="$emit('cancel')"> Hủy </Button>
				<Button
					class="ml-2"
					variant="solid"
					@click="$resources.getLinkPayment.submit()"
					:loading="$resources.getLinkPayment.loading"
				>
					Đến link thanh toán
				</Button>
			</div>
			<!-- <div v-if="step == 'Get Amount'">
        <Button
          variant="solid"
          @click="$resources.createPaymentIntent.submit()"
          :loading="$resources.createPaymentIntent.loading"
        >
          Tiếp theo
        </Button>
      </div>
      <div v-if="step == 'Add Card Details'">
        <Button @click="$emit('cancel')"> Hủy </Button>
        <Button
          class="ml-2"
          variant="solid"
          @click="onBuyClick"
          :loading="paymentInProgress"
        >
          Sang link thanh toán
        </Button>
      </div> -->
		</div>
	</div>
</template>
<script>
import PayOSLogo from '@/components/PayOSLogo.vue';
import { loadStripe } from '@stripe/stripe-js';
import { notify } from '@/utils/toast';

export default {
	name: 'BuyPrepaidCredits',
	components: {
		PayOSLogo
	},
	props: {
		minimumAmount: {
			default: 0
		}
	},
	mounted() {
		this.updateTotal();
	},
	watch: {
		creditsToBuy() {
			this.updateTotal();
		}
	},
	data() {
		return {
			step: 'Create order', // Get Amount / Add Card Details
			clientSecret: null,
			creditsToBuy: this.minimumAmount || null,
			total: this.minimumAmount,
			cardErrorMessage: null,
			errorMessage: null,
			paymentInProgress: false,
			infoOrder: null,
			checkFirstDeposit: undefined,
			cashPolicy: undefined,
			depositBonus: 0,
			textDepositBonus: null
		};
	},
	resources: {
		checkFirstDeposit() {
			return {
				url: 'press.api.billing.check_first_deposit',
				auto: true,
				async onSuccess(data) {
					this.checkFirstDeposit = data;
					this.updateTotal();
				},
				onError(e) {
					notify({
						title: 'Có lỗi xảy ra vui lòng thử lại.',
						color: 'red',
						icon: 'x'
					});
				}
			};
		},
		cashPolicy() {
			return {
				url: 'press.api.billing.get_cash_gift_policy',
				auto: true,
				async onSuccess(data) {
					this.cashPolicy = data;
					this.updateTotal();
				},
				onError(e) {
					notify({
						title: 'Có lỗi xảy ra vui lòng thử lại.',
						color: 'red',
						icon: 'x'
					});
				}
			};
		},
		createaOrder() {
			return {
				url: 'press.api.billing.create_order',
				params: {
					amount: this.creditsToBuy
				},
				validate() {
					this.errorMessage = null;
					if (this.creditsToBuy < this.minimumAmount) {
						let text = `Số tiền phải lớn hơn hoặc bằng ${this.$formatMoney(
							this.minimumAmount
						)} VND`;
						this.errorMessage = text;
						return text;
					} else if (this.creditsToBuy > 100000000) {
						let text = `Số tiền phải nhở hơn hoặc bằng ${this.$formatMoney(
							100000000
						)} VND`;
						this.errorMessage = text;
						return text;
					}
				},
				async onSuccess(data) {
					if (data.code == '00') {
						this.step = 'Get link payment';
						this.infoOrder = data.infoOrder;
					} else {
						notify({
							title: data.desc,
							color: 'red',
							icon: 'x'
						});
					}
				}
				// onError(e) {
				// 	notify({
				// 		title: 'Có lỗi xảy ra vui lòng thử lại.',
				// 		color: 'red',
				// 		icon: 'x'
				// 	});
				// }
			};
		},
		getLinkPayment() {
			return {
				url: 'press.api.billing.get_link_payment_payos',
				params: {
					info_order: this.infoOrder
				},
				async onSuccess(data) {
					if (data.code == '00') {
						this.step = 'Get link payment';
						window.location.href = data.infoPayment.checkoutUrl;
					} else {
						notify({
							title: data.desc,
							color: 'red',
							icon: 'x'
						});
					}
				},
				onError(e) {
					notify({
						title: 'Có lỗi xảy ra vui lòng thử lại.',
						color: 'red',
						icon: 'x'
					});
				}
			};
		},
		createPaymentIntent() {
			return {
				url: 'press.api.billing.create_payment_intent_for_buying_credits',
				params: {
					amount: Math.round(this.creditsToBuy)
				},
				validate() {
					if (this.creditsToBuy < this.minimumAmount) {
						return `Số tiền phải lớn hơn ${this.minimumAmount}`;
					}
				},
				async onSuccess(data) {
					this.step = 'Setting up Stripe';
					let { publishable_key, client_secret } = data;
					this.clientSecret = client_secret;
					this.stripe = await loadStripe(publishable_key);
					this.elements = this.stripe.elements();
					let theme = this.$theme;
					let style = {
						base: {
							color: theme.colors.black,
							fontFamily: theme.fontFamily.sans.join(', '),
							fontSmoothing: 'antialiased',
							fontSize: '13px',
							'::placeholder': {
								color: theme.colors.gray['400']
							}
						},
						invalid: {
							color: theme.colors.red['600'],
							iconColor: theme.colors.red['600']
						}
					};
					this.card = this.elements.create('card', {
						hidePostalCode: true,
						style: style,
						classes: {
							complete: '',
							focus: 'bg-gray-100'
						}
					});

					this.step = 'Add Card Details';
					this.$nextTick(() => {
						this.card.mount(this.$refs['card-element']);
					});

					this.card.addEventListener('change', event => {
						this.cardErrorMessage = event.error?.message || null;
					});
					this.card.addEventListener('ready', () => {
						this.ready = true;
					});
				}
			};
		}
	},
	methods: {
		formatAmount() {
			return this.$formatMoney(this.infoOrder.amount);
		},
		updateTotal() {
			if (
				this.checkFirstDeposit != undefined &&
				this.cashPolicy &&
				this.cashPolicy.length
			) {
				this.depositBonus = 0;
				let policy_type = 'Nạp lần đầu';
				if (this.checkFirstDeposit) {
					policy_type = 'Nạp thường';
				}

				let amount_prev = 0;
				for (let el of this.cashPolicy) {
					if (el.policy_type == policy_type) {
						if (
							this.creditsToBuy > amount_prev &&
							this.creditsToBuy < el.amount_from
						) {
							let amount_free =
								(el.amount_from * el.cash_gift_percentage) / 100;
							if (amount_free > el.maximum_amount) {
								amount_free = el.maximum_amount;
							}

							this.textDepositBonus = `Bạn được áp dụng khuyến mại nạp lần đầu. Nạp đạt mốc ${this.$formatMoney(
								el.amount_from
							)} VND để nhận thêm ${this.$formatMoney(amount_free)} VND`;

							if (this.checkFirstDeposit) {
								this.textDepositBonus = `Nạp đạt mốc ${this.$formatMoney(
									el.amount_from
								)} VND để nhận thêm ${this.$formatMoney(amount_free)} VND`;
							}
							break;
						} else {
							this.textDepositBonus = null;
							if (this.creditsToBuy >= el.amount_from) {
								let amount_free =
									(this.creditsToBuy * el.cash_gift_percentage) / 100;
								if (amount_free > el.maximum_amount) {
									amount_free = el.maximum_amount;
								}
								this.depositBonus = Math.round(amount_free);
							}
						}
						amount_prev = el.amount_to;
					}
				}
			}

			let value = String(this.creditsToBuy);
			this.total = Math.round(Number(value.replace(/^([^0-9]*)$/, '')));
		},
		setupStripe() {
			this.$resources.createPaymentIntent.submit();
		},
		async onBuyClick() {
			this.paymentInProgress = true;
			let payload = await this.stripe.confirmCardPayment(this.clientSecret, {
				payment_method: {
					card: this.card
				}
			});

			this.paymentInProgress = false;
			if (payload.error) {
				this.errorMessage = payload.error.message;
			} else {
				this.$emit('success');
				this.errorMessage = null;
				this.creditsToBuy = null;
			}
		}
	}
};
</script>
