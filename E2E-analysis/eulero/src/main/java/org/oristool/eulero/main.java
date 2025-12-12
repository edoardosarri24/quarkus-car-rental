package org.oristool.eulero;

import org.oristool.eulero.modeling.Activity;
import org.oristool.eulero.modeling.ModelFactory;
import org.oristool.eulero.modeling.Simple;
import org.oristool.eulero.modeling.stochastictime.UniformTime;
import org.oristool.eulero.evaluation.heuristics.SDFHeuristicsVisitor;
import org.oristool.eulero.evaluation.approximator.TruncatedExponentialMixtureApproximation;
import org.oristool.eulero.evaluation.heuristics.AnalysisHeuristicsVisitor;
import org.oristool.eulero.ui.ActivityViewer;
import org.oristool.eulero.evaluation.heuristics.EvaluationResult;
import org.oristool.eulero.modeling.stochastictime.HypoExponentialTime;
import org.oristool.eulero.modeling.stochastictime.HyperExponentialTime;
import org.oristool.eulero.modeling.stochastictime.ErlangTime;

import java.math.BigDecimal;
import java.math.BigInteger;
import java.util.List;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.io.IOException;

public class main {

    public static void main(String[] args) {
        System.err.println("executing the workflow analysis...");

        // Simple activities, the block of our model.

        // users
        Activity usersReserve = new Simple(
            "usersReserve",
            new HyperExponentialTime(
                new BigDecimal(4.530768718205648),
                new BigDecimal(0.13973653765949062),
                new BigDecimal(0.9700810661792936)));
        Activity usersStartParallel = new Simple(
            "usersStartParallel",
            new HyperExponentialTime(
                new BigDecimal(8.066047022030931),
                new BigDecimal(0.3600545266639021),
                new BigDecimal(0.9572691446236281)));
        Activity usersReservation = new Simple(
            "usersReservation",
            new HyperExponentialTime(
                new BigDecimal(4.524763329456558),
                new BigDecimal(0.10859317742426555),
                new BigDecimal(0.9765627407985986)));
        Activity usersReservationAll = new Simple(
            "usersReservationAll",
            new HyperExponentialTime(
                new BigDecimal(5.366932265271977),
                new BigDecimal(0.12074633548800023),
                new BigDecimal(0.9779968281175799)));
        Activity usersEnd = new Simple(
            "usersEnd",
            new HyperExponentialTime(
                new BigDecimal(0.8170246183204954),
                new BigDecimal(0.1694503875637973),
                new BigDecimal(0.8282263751711589)));

        // start-choice
        Activity startChoiceFirstChoice = new Simple(
            "startChoiceFirstChoice",
            new HyperExponentialTime(
                new BigDecimal(4.0926493316363475),
                new BigDecimal(0.27686777099379045),
                new BigDecimal(0.9366365288221127)));
        Activity startChoiceSecondChoice = new Simple(
            "startChoiceSecondChoice",
            new HyperExponentialTime(
                new BigDecimal(3.7459822168640264),
                new BigDecimal(0.16204722004810987),
                new BigDecimal(0.9585348005525391)));
        Activity startChoiceThirdChoice = new Simple(
            "startChoiceThirdChoice",
            new HyperExponentialTime(
                new BigDecimal(3.8120406591769647),
                new BigDecimal(0.24338725379486895),
                new BigDecimal(0.9399848156549986)));
        Activity startChoiceEnd = new Simple(
            "startChoiceEnd",
            new HyperExponentialTime(
                new BigDecimal(7.384692236993338),
                new BigDecimal(0.0800922478086917),
                new BigDecimal(0.9892706550374286)));

        // first-choice
        Activity firstChoice = new Simple(
            "firstChoice",
            new HyperExponentialTime(
                new BigDecimal(0.9042522685926947),
                new BigDecimal(0.19826383105851514),
                new BigDecimal(0.820171486728187)));

        // second-choice
        Activity secondChoice = new Simple(
            "secondChoice",
            new HyperExponentialTime(
                new BigDecimal(0.9229043043711354),
                new BigDecimal(0.21441813291147055),
                new BigDecimal(0.8114711133073416)));

        // third-choice
        Activity thirdChoice = new Simple(
            "thirdChoice",
            new HyperExponentialTime(
                new BigDecimal(0.9111875834829698),
                new BigDecimal(0.20981956726498377),
                new BigDecimal(0.8128294122611182)));

        // start-parallel
        Activity startParallel = new Simple(
            "startParallel",
            new HyperExponentialTime(
                new BigDecimal(9.522586481378232),
                new BigDecimal(0.7541702108833608),
                new BigDecimal(0.9266139859620057)));
        Activity startParallelEnd = new Simple(
            "startParallelEnd",
            new HyperExponentialTime(
                new BigDecimal(12.020114879210364),
                new BigDecimal(0.15853085549508875),
                new BigDecimal(0.9869828830767838)));

        // first-parallel
        Activity firstParallel = new Simple(
            "firstParallel",
            new HyperExponentialTime(
                new BigDecimal(1.0733139595631627),
                new BigDecimal(0.11028314651116178),
                new BigDecimal(0.9068237443762079)));

        // second-parallel
        Activity secondParallel = new Simple(
            "secondParallel",
            new HyperExponentialTime(
                new BigDecimal(1.0944662816332247),
                new BigDecimal(0.1262063535282602),
                new BigDecimal(0.8966091727684514)));

        // reservation
        Activity reservation = new Simple(
            "reservation",
            new HyperExponentialTime(
                new BigDecimal(0.7824875464931993),
                new BigDecimal(0.11315230564296974),
                new BigDecimal(0.8736631634098316)));
        Activity reservationAll = new Simple(
            "reservationAll",
            new HyperExponentialTime(
                new BigDecimal(0.48895761054260445),
                new BigDecimal(0.1384621598925262),
                new BigDecimal(0.7793149556054005)));

        // Model of the workflow.
        Activity model = ModelFactory.sequence(
            usersReserve,
            ModelFactory.XOR(List.of(0.2, 0.5, 0.3),
                ModelFactory.sequence(startChoiceFirstChoice, firstChoice),
                ModelFactory.sequence(startChoiceSecondChoice, secondChoice),
                ModelFactory.sequence(startChoiceThirdChoice, thirdChoice)),
            startChoiceEnd,
            usersStartParallel,
            startParallel,
            ModelFactory.forkJoin(firstParallel, secondParallel),
            startParallelEnd,
            usersReservation,
            reservation,
            usersReservationAll,
            reservationAll,
            usersEnd
        );

        // Analyze the model.
        AnalysisHeuristicsVisitor analyzer = new SDFHeuristicsVisitor(
            BigInteger.valueOf(2),
            BigInteger.valueOf(5),
            new TruncatedExponentialMixtureApproximation());
        double fairTimeTick = model.getLeastExpectedTimeTick();
        BigDecimal timeStep = BigDecimal.valueOf(fairTimeTick);
        //double fairTimeLimit = model.getFairTimeLimit();
        double fairTimeLimit = 170;
        double[] cdf = model.analyze(BigDecimal.valueOf(fairTimeLimit), timeStep, analyzer);

        // Save cdf to a CSV file
        try (PrintWriter writer = new PrintWriter(new FileWriter("../eulero_CDF.csv"))) {
            writer.println("time,cdf");
            for (int i = 0; i < cdf.length; i++) {
                double time = i * timeStep.doubleValue();
                writer.println(time + "," + cdf[i]);
            }
            System.out.println("CDF saved");
        } catch (IOException e) {
            e.printStackTrace();
        }

    }

}