<template>
	<div>
		<div v-if="step == 'Create order'" class="rounded-lg border p-4">
			<div class="text-md mb-3 font-bold">{{ $t('deposit_money') }}</div>
			<div>
				<FormControl
					class="mb-2"
					:label="$t('amount_of_money')"
					v-model.number="creditsToBuy"
					name="amount"
					autocomplete="off"
					type="number"
					:min="minimumAmount"
				/>
				<FormControl
					label=""
					disabled
					hidden
					v-model="total"
					name="total"
					autocomplete="off"
					type="number"
				/>
				<div class="mt-2 text-base">
					<table class="w-full text-sm">
						<tbody>
							<tr class="border-b">
								<td>{{ $t('deposit_balance') }}:</td>
								<td class="py-2 text-right">
									+ {{ this.$formatMoney(total) }} VND
								</td>
							</tr>
							<tr class="border-b">
								<td>{{ $t('promotional_balance_1') }}:</td>
								<td class="py-2 text-right">
									+ {{ this.$formatMoney(0) }} VND
								</td>
							</tr>
							<tr class="border-b">
								<td>{{ $t('promotional_balance_2') }}:</td>
								<td class="py-2 text-right">
									+ {{ this.$formatMoney(depositBonus) }} VND
								</td>
							</tr>
							<tr>
								<th>{{ $t('account_balance') }}:</th>
								<th class="py-2 text-right">
									+ {{ this.calcAmountAll() }} VND
								</th>
							</tr>
						</tbody>
					</table>
					<div class="my-4 text-sm" v-if="textDepositBonus">
						{{ textDepositBonus }}
					</div>
				</div>
				<ErrorMessage
					class="mt-2"
					:message="
						(['1', '2'].includes($resources.createaOrder.data?.code) &&
							$resources.createaOrder.data?.desc) ||
						errorMessage
					"
				/>
			</div>
		</div>
		<div
			v-if="$resources.cashPolicy.data?.length && step == 'Create order'"
			class="mt-5 rounded-lg border p-4"
		>
			<div class="text-md font-bold">{{ $t('bonus_policy') }}</div>
			<div>
				<div class="overflow-x-auto">
					<table class="text w-full text-sm">
						<thead>
							<tr class="text-gray-600">
								<th
									class="whitespace-nowrap border-b py-3 pr-2 text-left font-normal"
								>
									{{ $t('policy_type') }}
								</th>
								<th class="border-b py-3 pr-2 text-left font-normal">
									{{ $t('deposit_promotion') }}
								</th>
								<th class="border-b py-3 pr-2 text-left font-normal">
									% {{ $t('bonus_amount') }}
								</th>
							</tr>
						</thead>
						<tbody>
							<tr
								v-for="(row, i) in $resources.cashPolicy.data"
								:key="row.idx"
								:class="
									$resources.cashPolicy.data.length != i + 1 ? 'border-b' : ''
								"
							>
								<td class="py-3 pr-2">{{ row.policy_type }}</td>
								<td class="py-3 pr-2">
									{{ $t('top_up_from') }}
									{{ this.$formatMoney(row.amount_from) }} VND {{ $t('to') }}
									{{ this.$formatMoney(row.amount_to) }} VND
								</td>
								<td class="py-3 pr-2">
									{{ row.cash_gift_percentage }}% ({{ $t('maximum') }}
									{{ this.$formatMoney(row.maximum_amount) }} VND)
								</td>
							</tr>
						</tbody>
					</table>
				</div>
				<div v-if="$resources.cashPolicy.loading" class="py-20 text-center">
					<Button :loading="true">{{ $t('loading') }}</Button>
				</div>
			</div>
		</div>
		<router-link
			v-if="$resources.createaOrder.data?.code == 1"
			class="text-sm underline"
			to="transaction-history"
		>
			{{ $t('go_to_checkout') }}
		</router-link>
		<div v-if="infoOrder">
			<div>{{ $t('invoice_information_created') }}:</div>
			<div class="rounded-md border p-2">
				<p>{{ $t('invoice_code') }}: {{ infoOrder.order_code }}</p>
				<p>{{ $t('amount_of_money') }}: {{ formatAmount() }} VND</p>
				<p>{{ $t('content') }}: {{ infoOrder.description }}</p>
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
					{{ $t('create_invoice') }}
				</Button>
			</div>
			<div v-if="step == 'Get link payment'">
				<Button @click="$emit('cancel')"> {{ $t('cancel') }} </Button>
				<Button
					class="ml-2"
					variant="solid"
					@click="$resources.getLinkPayment.submit()"
					:loading="$resources.getLinkPayment.loading"
				>
					{{ $t('proceed_to_payment') }}
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
			minimumDefault: 10000,
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
						title: this.$t('an_error_occurred'),
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
						title: this.$t('an_error_occurred'),
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
					amount: this.creditsToBuy,
					lang: this.$i18n.locale
				},
				validate() {
					this.errorMessage = null;
					if (this.creditsToBuy < this.minimumDefault) {
						let text = `${this.$t(
							'buyprepaidcredit_content_1'
						)} ${this.$formatMoney(this.minimumDefault)} VND`;
						this.errorMessage = text;
						return text;
					} else if (this.creditsToBuy > 100000000) {
						let text = `${this.$t(
							'buyprepaidcredit_content_2'
						)} ${this.$formatMoney(100000000)} VND`;
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
					info_order: this.infoOrder,
					lang: this.$i18n.locale
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
						title: this.$t('an_error_occurred'),
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
		calcAmountAll() {
			let t = this.total + this.depositBonus;
			return this.$formatMoney(t);
		},
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

							this.textDepositBonus = `${this.$t(
								'buyprepaidcredit_content_3'
							)} ${this.$formatMoney(el.amount_from)} VND ${this.$t(
								'to_receive_more'
							)} ${this.$formatMoney(amount_free)} VND`;

							if (this.checkFirstDeposit) {
								this.textDepositBonus = `${this.$t(
									'threshold_reached'
								)} ${this.$formatMoney(el.amount_from)} VND ${this.$t(
									'to_receive_more'
								)} ${this.$formatMoney(amount_free)} VND`;
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
