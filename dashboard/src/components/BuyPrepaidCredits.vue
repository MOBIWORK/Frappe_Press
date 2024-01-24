<template>
	<div>
		<FormControl
			v-if="step == 'Create order'"
			class="mb-2"
			label="Tín dụng"
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
			label="Tổng số tiền + Thuế (nếu áp dụng)"
			disabled
			hidden
			v-model="total"
			name="total"
			autocomplete="off"
			type="number"
		/>
		<div class="mt-2 text-base">{{ this.$formatMoney(total) }} VND</div>

		<div v-if="step == 'Setting up Stripe'" class="mt-8 flex justify-center">
			<Spinner class="h-4 w-4 text-gray-600" />
		</div>
		<ErrorMessage
			class="mt-2"
			:message="
				$resources.createaOrder.data?.code == 1 &&
				$resources.createaOrder.data?.desc
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
// import StripeLogo from '@/components/StripeLogo.vue';
import PayOSLogo from '@/components/PayOSLogo.vue';
import { loadStripe } from '@stripe/stripe-js';
import { notify } from '@/utils/toast';

export default {
	name: 'BuyPrepaidCredits',
	components: {
		// StripeLogo,
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
			infoOrder: null
		};
	},
	resources: {
		createaOrder() {
			return {
				url: 'press.api.billing.create_order',
				params: {
					amount: this.creditsToBuy
				},
				validate() {
					if (this.creditsToBuy < this.minimumAmount) {
						return `Số tiền phải lớn hơn hoặc bằng ${this.minimumAmount}`;
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
					amount: this.creditsToBuy
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
			// if (this.$account.team.currency === 'INR') {
			// 	this.total = Number(
			// 		(
			// 			this.creditsToBuy +
			// 			this.creditsToBuy * this.$account.billing_info.gst_percentage
			// 		).toFixed(2)
			// 	);
			// } else {
			// 	this.total = this.creditsToBuy;
			// }
			this.total = this.creditsToBuy;
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
